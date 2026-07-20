from scripts.log_hook import sanitize_log_entry


def test_log_sanitizer_redacts_secrets_and_customer_pii() -> None:
    entry = {
        "student": "student@example.edu",
        "prompt": "Call 0912345678 or user@example.com with Bearer secret-token",
        "tool_input": {
            "api_key": "do-not-store-this",
            "command": "use ssmcp_abcdefghijklmnopqrstuvwxyz",
        },
    }

    sanitized = sanitize_log_entry(entry)

    assert sanitized["student"] == "student@example.edu"
    assert "0912345678" not in sanitized["prompt"]
    assert "user@example.com" not in sanitized["prompt"]
    assert "secret-token" not in sanitized["prompt"]
    assert sanitized["tool_input"]["api_key"] == "[REDACTED]"
    assert "ssmcp_" not in sanitized["tool_input"]["command"]
