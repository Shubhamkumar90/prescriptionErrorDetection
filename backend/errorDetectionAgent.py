import os
from google import genai
from dotenv import load_dotenv
import time
import json
load_dotenv()

client=genai.Client(api_key=os.getenv('GEMINI_API_KEY'))

# def error_detection_agent(structured_data: str):
#     print("-------Starting error detection Agent-----")
#     response = client.models.generate_content(
#         model="gemini-3-flash-preview",
#         contents="""
# You are a prescription error detection agent.

# INPUT DATA:"""+
# structured_data
# +""""
# TASK:
# Identify:
# - Dosage errors
# - Drug-drug interactions
# - Contraindications
# - Age/pregnancy/disease risks
# - Ambiguities and missing critical info

# OUTPUT FORMAT (STRICT JSON ONLY):
# {
#   "errors": [
#     {
#       "type": "",
#       "description": "",
#       "severity": "low | medium | high"
#     }
#   ]
# }

# RULES:
# - Be conservative
# - If patient context is missing, flag it as risk
# """
#     )
#     return response.text.strip()

# model = genai.GenerativeModel("gemini-1.5-flash")

def detect_prescription_errors(payload):

    prompt = f"""
You are a medical prescription safety checker.

Analyze this prescription payload and detect:

1. Dose errors
2. Unsafe frequency
3. Suspicious OCR drug mismatch
4. Toxicity concerns

Strict rules:

- Use extracted structured fields first.
- Use raw OCR line only to verify extracted dose or frequency when OCR ambiguity is obvious.
- Do NOT invent dosage if unclear.
- If extracted frequency contains meal instruction words (before food, after food, with food), separate meal instruction from dosing repetition.
- Do not convert meal instruction alone into numeric frequency.
- Calculate frequency only when meal repetition is explicitly stated (e.g. after breakfast and dinner, after each meal, before lunch).
- Only mention OCR drug mismatch when confidence is low or corrected drug remains uncertain.
- If dosage is missing or unclear, check raw OCR only when the number is clearly readable, if not present then assume safe range and do not flag dose error and mention that the dosage not specified, assumed dosages.
- Only flag dose when clearly abnormal for the detected drug.
- Do not infer instruction unless obvious from raw OCR line.
- Use toxicity and indication only as supporting evidence.
- Do not hallucinate missing medical facts.
- If everything appears acceptable, return issue = "No obvious safety concern identified".
- If multiple issues exist for one drug, combine them inside one object only.
- Do not mention raw OCR text in explanation unless the issue itself is OCR drug mismatch.
- Only mention OCR error only if the confidence is below 70

Prescription:
{json.dumps(payload, indent=2)}

Return strict JSON:
{{
  "drug_analysis": [
    {{
      "drug": "",
      "issue": "",
      "severity": "High"|"Medium"|"Low"|"None",
      "explanation": ""
    }}
  ],
  "user_explanation": ""
}}
Rules for user_explanation:
- This must be a clear, simple, human-friendly summary for a non-medical user.
- Do NOT mention technical terms like OCR, payload, or extraction.
- Do NOT repeat raw drug-level explanations.
- Summarize overall safety:
    • If any High severity → warn clearly (serious concern)
    • If Medium → mention caution
    • If Low → say minor issues or missing details
    • If None → say prescription appears safe
- Mention key types of issues briefly (e.g., missing frequency, unclear dosage)
- Keep it short (2–4 sentences max)
- Do not mention drug names unless necessary
- Be calm and informative, not alarming unless severity is High
"""

    # response = client.models.generate_content(model="gemini-3-flash-preview",contents=prompt)

    # return response.text
    for attempt in range(3):
        try:
            response = client.models.generate_content(
                model="gemini-3-flash-preview",
                contents=prompt
            )
            clean = response.text.replace("```json", "").replace("```", "").strip()
            error = json.loads(clean)
            return error

        except Exception as e:
            if attempt < 2:
                time.sleep(3)
            else:
                return {
                    "drug_analysis": [
                        {
                            "drug": "System",
                            "issue": "LLM service unavailable",
                            "severity": "Low",
                            "explanation": "Temporary model overload. Please try again."
                        }
                    ],
                    "user_explanation": "We could not fully analyze the prescription due to a temporary system issue. Please try again."
                }