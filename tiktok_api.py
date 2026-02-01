from typing import Tuple, Optional, Dict
import oauth


def _error(code: str, message: str, action: str, retryable: bool) -> Dict:
    return {"code": code, "message": message, "action": action, "retryable": retryable}

# Validation of Music id
def validate_music_id(music_id: str) -> Tuple[bool, Optional[Dict]]:
    if not music_id:
        return False, _error("missing_music_id", "Music ID missing", "Provide a valid music ID or upload music", True)

    if music_id.startswith("music_"):
        return True, None

    return False, _error("invalid_music_id", "Music ID not found or not approved", "Check music ID or upload a new music file", True)


def upload_music() -> str:
    # Simulate an upload that returns a valid music id
    return "music_uploaded_456"

#  Submission & API Failure Reasoning

def submit_ad(payload: dict, token: str) -> Tuple[bool, Optional[Dict]]:
    # Invalid OAuth token
    valid, err = oauth.validate_token(token)
    if not valid:
        return False, err

    # Business rule: Conversions requires music
    if payload["objective"] == "Conversions" and not payload["creative"].get("music_id"):
        return False, _error("missing_music_for_conversions", "Music is REQUIRED for Conversions objective", "Add a valid music ID or upload music", True)

    # If music id is present, validate it
    music_id = payload["creative"].get("music_id")
    if music_id:
        ok, merr = validate_music_id(music_id)
        if not ok:
            return False, merr

    # Simulated geo restriction
    if payload.get("campaign_name") and payload["campaign_name"].lower().startswith("india"):
        return False, _error("geo_restriction", "403 Geo-restriction: Ads not allowed in this region", "Target a different region or change campaign targeting", False)

    return True, {"message": "Ad submitted successfully"}
