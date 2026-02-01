import os
import time
from typing import Tuple, Optional, Dict


# Mock token store (in-memory)

_TOKEN_STORE = {}


def _error(code: str, message: str, action: str, retryable: bool) -> Dict:
    return {"code": code, "message": message, "action": action, "retryable": retryable}


def get_access_token(user_name: str) -> Tuple[Optional[str], Optional[Dict]]:
    """Issues a mock OAuth access token after validating env credentials.

    Returns (token, None) on success or (None, error_dict) on failure.
    """
    if not user_name or len(user_name.strip()) < 2:
        return None, _error("invalid_user", "Invalid user identity provided", "Provide a valid user name (min 2 chars)", False)

    client_id = os.getenv("TIKTOK_CLIENT_ID")
    client_secret = os.getenv("TIKTOK_CLIENT_SECRET")

    # ENV validation
    if not client_id:
        return None, _error("missing_env", "TIKTOK_CLIENT_ID missing in environment", "Add TIKTOK_CLIENT_ID to .env", False)
    if not client_secret:
        return None, _error("missing_env", "TIKTOK_CLIENT_SECRET missing in environment", "Add TIKTOK_CLIENT_SECRET to .env", False)

    # Credential validation (mock)
    if client_id != "test_client_id":
        return None, _error("invalid_client_id", "Invalid TikTok client_id", "Check TIKTOK_CLIENT_ID in .env", False)

    # Support a special secret value to simulate missing Ads scope
    if client_secret == "test_client_secret_noscope":
        token = f"mock_token_{user_name}_{int(time.time())}::scopes="
        _TOKEN_STORE[token] = {
            "user": user_name,
            "issued_at": time.time(),
            "expires_in": 300, #5 minutes
            "revoked": False
        }
        return token, None

    if client_secret != "test_client_secret":
        return None, _error("invalid_client_secret", "Invalid TikTok client_secret", "Check TIKTOK_CLIENT_SECRET in .env", False)

    # Issue token with Ads scope
    token = f"mock_token_{user_name}_{int(time.time())}::scopes=ads"

    _TOKEN_STORE[token] = {
        "user": user_name,
        "issued_at": time.time(),
        "expires_in": 300,  # 5 minutes
        "revoked": False
    }

    return token, None

# Token Validattion
def validate_token(token: str) -> Tuple[bool, Optional[Dict]]:
    """Validates access token and returns structured errors when relevant."""
    if not token:
        return False, _error("missing_token", "Missing OAuth access token", "Authenticate to obtain an access token", True)

    token_data = _TOKEN_STORE.get(token)

    if not token_data:
        return False, _error("invalid_token", "Invalid or unknown access token", "Re-authenticate to obtain a new token", True)

    # Revocation check
    if token_data["revoked"]:
        return False, _error("revoked_token", "Token has been revoked", "Re-authenticate to obtain a new token", True)

    # Expiry check
    current_time = time.time()
    if current_time - token_data["issued_at"] > token_data["expires_in"]:
        return False, _error("expired_token", "Access token has expired", "Re-authenticate to refresh the token", True)

    # Scope check
    if "scopes=" in token:
        # Simple parsing of the mock token
        parts = token.split("::")
        if len(parts) > 1 and "scopes=" in parts[1]:
            scopes = parts[1].split("=")[1]
            if "ads" not in scopes:
                return False, _error("missing_scope", "Missing Ads permission scope", "Re-authenticate and grant Ads permission to the app", True)

    return True, None

# revoke_token
def revoke_token(token: str):
    """Explicitly revoke a token (simulates user logout / permission removal)."""
    if token in _TOKEN_STORE:
        _TOKEN_STORE[token]["revoked"] = True


def format_error(err: Dict) -> str:
    return f"{err['message']}. Suggested action: {err['action']}"
