from llm import ask_gemini
from schema import AdSchema
from oauth import get_access_token, validate_token, format_error
from tiktok_api import validate_music_id, upload_music, submit_ad
from dotenv import load_dotenv
import json

load_dotenv()

# Model
def ai(msg):
    print(f"\n AI : {msg}")

# User
def user(msg):
    return input(f"\n USER : {msg}: ")
# Above Two function I Used as a CLI

def prompt_until(prompt_text, validate_fn, error_msg, max_attempts=5):
    attempts = 0
    while attempts < max_attempts:
        val = user(prompt_text)
        if validate_fn(val):
            return val
        attempts += 1
        ai(error_msg)
    raise ValueError(f"Failed to get valid input for {prompt_text}")

# Campaign Name (Required, min 3 chars)
def get_campaign_name():
    def valid_name(v):
        return v and len(v.strip()) >= 3

    return prompt_until(
        "Campaign name (min 3 chars)",
        valid_name,
        "Campaign name must be at least 3 characters."
    )

# Objective (Traffic or Conversions)
def choose_objective():
    def valid_obj(v):
        return v and v.capitalize() in ["Traffic", "Conversions"]

    obj = prompt_until(
        "Objective (Traffic / Conversions)",
        valid_obj,
        "Objective must be 'Traffic' or 'Conversions' (case-insensitive)."
    )
    return obj.capitalize()

# Ad Text (Required, max 100 chars)
def get_ad_text():
    def valid_text(v):
        return v and len(v) <= 100

    return prompt_until(
        "Ad text (max 100 chars)",
        valid_text,
        "Ad text required and must be 100 characters or fewer."
    )

# CTA (Required)
def get_cta():
    def valid_cta(v):
        return v and len(v.strip()) > 0

    return prompt_until(
        "CTA",
        valid_cta,
        "CTA is required. Provide a short CTA text."
    )

# Music Option (Conditional logic required)
def handle_music_flow(objective):
    """Return a valid music_id or None."""
    wants = user("Add music? (yes/no)")
    if wants.lower() != "yes":
        if objective == "Conversions":
            ai("Conversions objective requires music. Please choose to add or upload music.")
            return handle_music_flow(objective)
        return None
    # Cases for Music id
    choice = user("Existing or Upload (existing/upload)")
    if choice.lower() == "existing":
        while True:
            mid = user("Enter music ID")
            ok, err = validate_music_id(mid)
            if ok:
                return mid
            # Explain Error by help of llm and offer options
            ai(ask_gemini(
                "You are a TikTok Ads expert.",
                f"Music validation failed: {err}. Explain and suggest next steps."
            ))
            next_step = user("Choose: retry / upload / cancel")
            if next_step.lower() == "retry":
                continue
            if next_step.lower() == "upload":
                mid = upload_music()
                ai(f"Uploaded music ID: {mid}")
                ok2, err2 = validate_music_id(mid)
                if ok2:
                    return mid
                ai(ask_gemini(
                    "You are a TikTok Ads expert.",
                    f"Uploaded music validation failed: {err2}. Explain and suggest next steps."
                ))
                # loop back to ask what to do
            if next_step.lower() == "cancel":
                if objective == "Conversions":
                    ai("Cannot cancel music when objective is Conversions. Please add music.")
                    continue
                return None
    else:
        # Upload flow
        mid = upload_music()
        ai(f"Uploaded music ID: {mid}")
        ok, err = validate_music_id(mid)
        if ok:
            return mid
        ai(ask_gemini(
            "You are a TikTok Ads expert.",
            f"Uploaded music validation failed: {err}. Explain and suggest next steps."
        ))
        # give user options
        next_step = user("Choose: retry_upload / enter_existing / cancel")
        if next_step.lower() == "retry_upload":
            return handle_music_flow(objective)
        if next_step.lower() == "enter_existing":
            return handle_music_flow(objective)
        if next_step.lower() == "cancel":
            if objective == "Conversions":
                ai("Conversions objective requires music. Cannot cancel.")
                return handle_music_flow(objective)
            return None


def main():
    ai("Starting TikTok Ads AI Agent")

    # conversation transcript and internal reasoning logs
    transcript = []
    reasoning = []

    user_name = user("Enter your name")
    transcript.append({"user_name": user_name})

    token, error = get_access_token(user_name)
    if error:
        explanation = ask_gemini(
            "You are an OAuth expert.",
            f"Explain this OAuth error clearly and suggest a fix: {format_error(error)}"
        )
        ai(explanation)
        return

    valid, error = validate_token(token)
    if not valid:
        explanation = ask_gemini(
            "You are an OAuth expert.",
            f"Explain token error and corrective action: {format_error(error)}"
        )
        ai(explanation)
        return

    ad = AdSchema()

    # Collect inputs with validation
    ad.data["campaign_name"] = get_campaign_name()
    reasoning.append("Campaign name validated")

    ad.data["objective"] = choose_objective()
    reasoning.append(f"Objective set to {ad.data['objective']}")

    ad.data["creative"]["text"] = get_ad_text()
    reasoning.append("Ad text validated")

    ad.data["creative"]["cta"] = get_cta()
    reasoning.append("CTA validated")

    # MUSIC logic
    ad.data["creative"]["music_id"] = handle_music_flow(ad.data["objective"])
    reasoning.append(f"Music flow completed; music_id={ad.data['creative']['music_id']}")

    # Final rule validation just in case
    errors = ad.validate_rules()
    if errors:
        ai(ask_gemini(
            "You are an ads validation expert.",
            f"Explain these validation errors clearly and suggest fixes: {errors}"
        ))
        return

    # Attempt submission with intelligent error handling
    attempt = 0
    while attempt < 3:
        success, result = submit_ad(ad.data, token)
        if success:
            ai("Ad submitted successfully!")
            ai(ask_gemini(
                "You are an assistant that summarizes structured output.",
                f"Explain this final ad payload in simple words:\n{ad.data}"
            ))
            print("_" * 50)
            print("\n FINAL AD PAYLOAD\n")
            print(json.dumps(ad.data, indent=2))
            return

        # result is an error dict
        ai(ask_gemini(
            "You are a TikTok Ads API expert.",
            f"Submission failed: {result['message']}. Suggested action: {result['action']}"
        ))

        # Decide action based on error code
        code = result.get("code")
        if code in ("invalid_token", "expired_token", "missing_scope"):
            ai("Attempting to re-authenticate to resolve token issue...")
            user_name = user("Re-enter your name to re-authenticate")
            token, err = get_access_token(user_name)
            if err:
                ai(ask_gemini(
                    "You are an OAuth expert.",
                    f"Re-authentication failed: {format_error(err)}"
                ))
                return
            valid, err = validate_token(token)
            if not valid:
                ai(ask_gemini(
                    "You are an OAuth expert.",
                    f"Token validation after re-authentication failed: {format_error(err)}"
                ))
                return
            attempt += 1
            continue

        if code == "missing_music_for_conversions":
            ai("Please add or upload music to satisfy the Conversions objective.")
            ad.data["creative"]["music_id"] = handle_music_flow(ad.data["objective"])
            attempt += 1
            continue

        if code == "invalid_music_id":
            ai("Music ID invalid. Please re-check or upload a new music file.")
            ad.data["creative"]["music_id"] = handle_music_flow(ad.data["objective"])
            attempt += 1
            continue

        if code == "geo_restriction":
            ai("This campaign is blocked due to geo-restriction and cannot be submitted. Change campaign name or target region.")
            return

        # Unhandled error
        ai("An unrecoverable error occurred. See the message above for details.")
        return

if __name__ == "__main__":
    main()
