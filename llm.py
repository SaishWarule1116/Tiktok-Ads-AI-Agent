import os
from dotenv import load_dotenv

# Import the new google.genai library consistently.
# Ensure 'google-generativeai' (the package for google.genai) is installed.
import google.genai as genai

load_dotenv()

API_KEY = GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')

# Initialize client only if API_KEY is available
client = None
REAL_GENAI = False
if API_KEY:
    try:
        client = genai.Client(api_key=API_KEY)
        REAL_GENAI = True
    except Exception as e:
        print(f"Error initializing Google GenAI client: {e}. Falling back to stubbed LLM.")
else:
    print("Warning: GOOGLE_API_KEY not found. Falling back to stubbed LLM.")

## Basic deterministic, helpful fallback for development/testing

def _stub_response(system_prompt: str, user_prompt: str) -> str:
    if "OAuth" in system_prompt or "OAuth" in user_prompt:
        return "[SIMULATED LLM] The OAuth error indicates invalid credentials or missing permissions. Suggested action: Verify your TikTok app credentials or re-authenticate granting Ads permission."
    if "validation" in system_prompt.lower() or "validation" in user_prompt.lower():
        return "[SIMULATED LLM] Validation failed. Check the provided fields and follow the suggested corrective actions."
    if "summarize" in system_prompt.lower() or "structured output" in system_prompt.lower():
        return f"[SIMULATED LLM] Summary: {user_prompt}"
    # Default echo-like response
    return f"[SIMULATED LLM] {user_prompt}"


def ask_gemini(system_prompt: str, user_prompt: str) -> str:
    """Return a human-friendly explanation from the LLM or a stubbed response if the client is not available."""
    if REAL_GENAI and client:
        response = client.models.generate_content(
            model=os.getenv("GEMINI_MODEL", "models/gemini-flash-latest"), 
            contents=user_prompt,
            config={
                'system_instruction': system_prompt
            }
        )
        return getattr(response, "text", str(response))
    else:
        return _stub_response(system_prompt, user_prompt)
