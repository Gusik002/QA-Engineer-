import re


def normalize_phone_number(phone: str | None) -> str:
    """
    Normalise Azercell-style phone numbers.

    Examples:
    - "0501234567"   -> "501234567"
    - "50 123 45 67" -> "501234567"
    - "+994501234567"-> "501234567"
    """
    if phone is None:
        return ""
    digits = re.sub(r"\D", "", str(phone))
    if digits.startswith("0"):
        digits = digits[1:]
    # strip country code 994 if present
    if digits.startswith("994") and len(digits) > 9:
        digits = digits[3:]
    return digits