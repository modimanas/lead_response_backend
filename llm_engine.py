import os
import json
from dotenv import load_dotenv
from groq import Groq

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

MODEL_NAME = "llama-3.1-8b-instant"


# -------------------------
# Safe JSON Parser
# -------------------------

def safe_json(response):
    try:
        content = response.choices[0].message.content
        # Try to extract JSON if it's wrapped in text
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0]
        elif "{" in content:
            content = content[content.find("{"):content.rfind("}")+1]
        return json.loads(content)
    except Exception as e:
        return {"error": f"invalid_json: {str(e)}"}


# -------------------------
# 1️⃣ Intent & Hypothesis Generation
# -------------------------

def extract_intent_and_hypotheses(message):
    """Extract the problem and generate initial hypotheses"""
    prompt = f"""
You are a diagnostic expert who listens to problems and figures out what might be wrong.

Analyze what the user is telling you and:
1. Understand the core problem in simple terms
2. Generate 3-4 possible reasons WHY this is happening
3. For each reason, estimate how likely it is (higher % = more confident)
4. Rate the urgency: low/moderate/high

User's problem:
"{message}"

Think like:
- What are the most common causes of this issue?
- Which one seems most likely given what they said?
- Are any of these dangerous/urgent?

Return ONLY valid JSON:
{{
    "main_issue": "simple 1-sentence problem description",
    "risk_level": "low/moderate/high",
    "hypotheses": [
        {{
            "name": "simple cause name",
            "description": "why this might be happening (plain English)",
            "probability": 0.6,
            "key_evidence": ["things that would prove this", "things that would disprove this"]
        }}
    ]
}}
"""

    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3
    )

    return safe_json(response)


# -------------------------
# 2️⃣ Hypothesis-Driven Question Generator
# -------------------------

def generate_adaptive_question(original_issue, hypotheses, answers_history, asked_questions):
    """Generate a smart, context-aware question like ChatGPT"""
    
    # Sort hypotheses by likelihood
    sorted_hyp = sorted(hypotheses, key=lambda x: x["probability"], reverse=True)
    top_1 = sorted_hyp[0] if len(sorted_hyp) > 0 else {}
    top_2 = sorted_hyp[1] if len(sorted_hyp) > 1 else {}
    
    # Analyze conversation to understand what we know
    answers_summary = "\n".join([
        f"- {h['answer']}"
        for h in answers_history[-3:]  # Last 3 answers for context
    ]) if answers_history else "Just started"
    
    # Get list of facts we already know
    facts_known = set()
    for answer in answers_history:
        facts_known.add(answer['answer'].lower())
    
    # Detect domain
    health_keywords = ["vomiting", "headache", "fever", "pain", "sick", "ill", "symptom", "dizzy", "nausea", "feeling", "health", "disease", "hurt", "ache", "cough", "fatigue"]
    original_lower = original_issue.lower()
    is_health = any(keyword in original_lower for keyword in health_keywords)
    
    domain = "HEALTH/MEDICAL" if is_health else "TECHNICAL/HOME/GENERAL"
    
    prompt = f"""
You are a smart diagnostic AI like ChatGPT. Act like a helpful expert having a natural conversation.

CONTEXT:
- Issue: {original_issue}
- Domain: {domain}
- Questions already asked: {len(asked_questions)}
- Top 2 hypotheses:
  1. {top_1.get('name', 'Unknown')} ({top_1.get('probability', 0):.0%})
  2. {top_2.get('name', 'Unknown')} ({top_2.get('probability', 0):.0%})

What we know so far:
{answers_summary}

Questions ALREADY ASKED (NEVER REPEAT THESE):
{chr(10).join('- ' + q for q in (asked_questions or [])) if asked_questions else "None yet"}

YOUR JOB:
Generate ONE clever follow-up question that:
1. Act natural and conversational - like you're learning as you go
2. Is COMPLETELY DIFFERENT from questions already asked
3. Narrows down between top 2 hypotheses
4. Asks about OBSERVABLE FACTS only
5. Flows naturally from the conversation
6. Gets information we DON'T have yet

SMART QUESTION STRATEGY:
- If we know "started 2 weeks ago", don't ask about timing again
- If we know "worse after rain", don't ask about weather again
- Ask about the NEXT logical thing: other symptoms, context, patterns, triggers
- Make it conversational: "So you mentioned X... Does Y happen too?"

Think about what distinguishes {top_1.get('name', '')} vs {top_2.get('name', '')}:
- What evidence would support one over the other?
- What do we still NOT know?
- Ask about that!

Generate a SINGLE smart question that:
- Is natural and conversational
- Asks something NEW we haven't covered
- Will help distinguish between the top hypotheses
- Provides 3-4 realistic observable options

Return ONLY valid JSON (no markdown, no code blocks):
{{
    "question": "your smart conversational question",
    "options": ["option 1", "option 2", "option 3"],
    "reasoning": "why this question helps narrow it down"
}}
"""

    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7  # Higher temp for more creative/natural questions
    )

    return safe_json(response)


# -------------------------
# 3️⃣ Adaptive Hypothesis Updater
# -------------------------

def update_hypotheses(original_issue, hypotheses, last_question, last_answer):
    """Update hypothesis probabilities based on the latest answer"""
    
    hyp_text = "\n".join([
        f"- {h['name']}: {h['description']} (current: {h['probability']:.0%})"
        for h in hypotheses
    ])
    
    prompt = f"""
You are a Bayesian reasoning expert. Given the latest answer, update the probability of each hypothesis.

Issue: {original_issue}

Current Hypotheses:
{hyp_text}

Latest Question: {last_question}
Latest Answer: {last_answer}

For each hypothesis:
1. Does this answer support it? How much?
2. Does this answer contradict it?
3. What's the new probability? (0.0 to 1.0)

Return ONLY valid JSON:
{{
    "updated_hypotheses": [
        {{
            "name": "hypothesis name",
            "new_probability": 0.7,
            "reasoning": "why probability changed"
        }}
    ]
}}
"""

    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2
    )

    result = safe_json(response)
    
    # Update hypothesis probabilities
    if "updated_hypotheses" in result:
        for update in result["updated_hypotheses"]:
            for hyp in hypotheses:
                if hyp["name"].lower() == update["name"].lower():
                    hyp["probability"] = update.get("new_probability", hyp["probability"])
    
    return hypotheses


# -------------------------
# 4️⃣ Improved Confidence Evaluation
# -------------------------

def evaluate_confidence(original_issue, hypotheses, answers_count, issue_type="general"):
    """Evaluate if we have enough confidence to provide a diagnosis"""
    
    # Sort by probability
    sorted_hyp = sorted(hypotheses, key=lambda x: x["probability"], reverse=True)
    
    top_prob = sorted_hyp[0]["probability"] if sorted_hyp else 0
    second_prob = sorted_hyp[1]["probability"] if len(sorted_hyp) > 1 else 0
    
    # Different thresholds for different issue types
    thresholds = {
        "health": {"min_confidence": 0.85, "min_questions": 4, "gap": 0.40},
        "medical": {"min_confidence": 0.85, "min_questions": 4, "gap": 0.40},
        "safety": {"min_confidence": 0.80, "min_questions": 3, "gap": 0.35},
        "general": {"min_confidence": 0.70, "min_questions": 2, "gap": 0.25},
        "tech": {"min_confidence": 0.65, "min_questions": 2, "gap": 0.20},
    }
    
    # Detect if it's a health issue
    health_keywords = ["vomiting", "headache", "fever", "pain", "sick", "ill", "symptom", "dizzy", "nausea", "feeling", "health", "disease", "hurt", "ache"]
    original_lower = original_issue.lower()
    is_health = any(keyword in original_lower for keyword in health_keywords)
    if is_health:
        issue_type = "health"
    
    config = thresholds.get(issue_type, thresholds["general"])
    min_confidence = config["min_confidence"]
    min_questions = config["min_questions"]
    min_gap = config["gap"]
    
    prompt = f"""
You are deciding if we have enough information to give final advice.

Issue Type: {issue_type.upper()}
Original Issue: {original_issue}

Top hypothesis: {sorted_hyp[0]['name'] if sorted_hyp else 'unknown'} (confidence: {top_prob:.0%})
Second best: {sorted_hyp[1]['name'] if len(sorted_hyp) > 1 else 'none'} (confidence: {second_prob:.0%})
Confidence gap: {(top_prob - second_prob):.0%}
Questions asked so far: {answers_count}

THRESHOLDS for {issue_type.upper()} issues:
- Minimum confidence needed: {min_confidence:.0%}
- Minimum questions needed: {min_questions}
- Confidence gap needed: {min_gap:.0%}

CRITICAL RULE for HEALTH issues:
- NEVER give medical advice with less than {min_questions} questions
- ALWAYS recommend seeing a professional if any doubt
- Better to ask 1 more question than to give bad advice

STOP (give final advice) only when ALL of these are true:
1. Confidence >= {min_confidence:.0%}
2. Questions asked >= {min_questions}
3. Gap between top 2 >= {min_gap:.0%}

KEEP ASKING if ANY of these are true:
- Confidence < {min_confidence:.0%}
- Questions < {min_questions}
- Gap < {min_gap:.0%}

Return ONLY valid JSON:
{{
    "confidence_score": 0.75,
    "verdict": "CONTINUE or STOP",
    "reasoning": "why this decision"
}}
"""

    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2
    )

    result = safe_json(response)
    return result


# -------------------------
# 5️⃣ Evidence-Based Final Response
# -------------------------

def generate_final_response(original_issue, hypotheses, answers_history, risk_level):
    """Generate SHORT final diagnosis - 2-3 sentences maximum"""
    
    # Detect if this is a health issue
    health_keywords = ["vomiting", "headache", "fever", "pain", "sick", "ill", "symptom", "dizzy", "nausea", "feeling", "health", "disease", "hurt", "ache", "cough", "fatigue"]
    original_lower = original_issue.lower()
    is_health = any(keyword in original_lower for keyword in health_keywords)
    
    # Sort hypotheses by probability
    sorted_hyp = sorted(hypotheses, key=lambda x: x["probability"], reverse=True)
    top_hypothesis = sorted_hyp[0] if sorted_hyp else {}
    top_name = top_hypothesis.get('name', 'Unknown')
    
    health_disclaimer_text = "⚠️ See a doctor. " if is_health else ""
    
    # VERY strict format - force concise output
    prompt = f"""FINAL ANSWER: 2-3 SHORT SENTENCES. NO QUESTIONS. NO LISTS.

Diagnosis: {top_name}
Issue: {original_issue}

Rules:
- Write STATEMENTS, not questions
- Keep each sentence SHORT (under 20 words)
- DO NOT ask questions
- Only give advice/conclusion

Format:
"Yeah, probably [cause]. [Why/what to do]. [Action or professional help]."

{health_disclaimer_text}

WRITE NOW (statements only, 2-3 sentences):"""

    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.15  # Very low temp for consistency
    )

    result = response.choices[0].message.content.strip()
    
    # Post-processing: Remove numbering, clean up, remove questions
    lines = result.split('\n')
    cleaned = []
    for line in lines:
        line = line.strip()
        
        # Remove numbering like "1." "2." etc or "[Sentence 1]:"
        if '[' in line and ']' in line and ':' in line:
            idx = line.rfind(':')
            if idx > 0:
                line = line[idx+1:].strip()
        elif line and line[0].isdigit() and line[1] in '.)':
            line = line[2:].strip()
        
        # Skip instructions or empty lines or questions
        if (line and 
            not line.startswith('Keep') and 
            not line.startswith('Note') and 
            not line.startswith('-') and
            not line.endswith('?')):
            cleaned.append(line)
    
    # Return first 3 lines max
    final = " ".join(cleaned[:3])  # Use space instead of newline for compact output
    
    # Fallback if too short
    if not final or len(final) < 15:
        final = f"Yeah, probably {top_name}. Check recent conditions. Consider professional help if it persists."
    
    return final
