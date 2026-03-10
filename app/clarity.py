def clarity_score(text: str):
    text = text.lower()
    score = 0

    # Persona / Target
    if any(word in text for word in [
        "startup", "founder", "agency", "enterprise",
        "smb", "creator", "developer"
    ]):
        score += 1

    # Market Type
    if any(word in text for word in ["b2b", "b2c"]):
        score += 1

    # Clear Problem
    if len(text.split()) > 6:
        score += 1

    # Domain specificity
    if any(word in text for word in [
        "tax", "compliance", "marketing", "automation",
        "analytics", "finance", "health", "legal"
    ]):
        score += 1

    # Geography signal
    if any(word in text for word in [
        "india", "us", "uk", "europe", "global"
    ]):
        score += 1

    return score
