"""
Data Privacy, Secret Masking, and Redaction Utility for Event Payloads.
Enforces that API keys, passwords, bearer tokens, and PII are never leaked into the ledger.
"""
import re
from typing import Any, Dict, List, Set

SENSITIVE_KEY_PATTERNS = {
    "api_key",
    "apikey",
    "secret",
    "password",
    "access_token",
    "refresh_token",
    "auth_token",
    "authorization",
    "bearer",
    "private_key",
    "credentials",
    "cookie",
}

EMAIL_REGEX = re.compile(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+")


def is_sensitive_key(key: str) -> bool:
    key_lower = key.lower().replace("-", "_")
    return any(pattern in key_lower for pattern in SENSITIVE_KEY_PATTERNS)


def redact_data(data: Any, level: str = "sanitized") -> Any:
    """
    Recursively sanitize dictionaries, lists, and strings based on redaction level:
    - metadata_only: strips payload values to summary metrics/keys.
    - sanitized: recursively masks credentials, tokens, and PII.
    - full_content: keeps detailed content but still strictly masks credentials.
    """
    if level == "metadata_only":
        if isinstance(data, dict):
            return {
                k: "[METADATA_ONLY]" if not isinstance(v, (int, float, bool)) and k not in {"model", "status", "version", "event"} else v
                for k, v in data.items()
                if not is_sensitive_key(k)
            }
        elif isinstance(data, list):
            return [f"<{len(data)} items>"]
        return data

    if isinstance(data, dict):
        sanitized_dict = {}
        for k, v in data.items():
            if is_sensitive_key(k):
                sanitized_dict[k] = "[REDACTED_CREDENTIAL]"
            else:
                sanitized_dict[k] = redact_data(v, level=level)
        return sanitized_dict

    elif isinstance(data, list):
        return [redact_data(item, level=level) for item in data]

    elif isinstance(data, str):
        # Mask emails and API key looking strings (e.g. sk-..., bearer tokens)
        if "sk-" in data or "Bearer " in data:
            return "[REDACTED_TOKEN]"
        if EMAIL_REGEX.search(data):
            return EMAIL_REGEX.sub("[REDACTED_EMAIL]", data)
        return data

    return data
