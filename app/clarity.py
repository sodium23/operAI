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

    # Clear Problem Length
    if len(text.split()) > 6:
        score += 1

    # Domain Specificity
    if any(word in text for word in [
        "tax", "compliance", "marketing",
        "automation", "analytics",
        "finance", "health", "legal"
    ]):
        score += 1

    # Geography Signal
    if any(word in text for word in [
        "india", "us", "uk", "europe", "global"
    ]):
        score += 1

    return score


def next_question(count: int):

    questions = [
        "Who is the primary target user?",
        "Is this B2B or B2C?",
        "What exact problem are you solving?",
        "How will this make money?",
        "What platform will this run on?",
        "Is this MVP validation or long-term SaaS?",
        "Geographic focus?",
        "Any regulatory sensitivity?",
        "What differentiates this?",
        "What resources do you currently have?"
    ]

    if count < len(questions):
        return questions[count]

    return None
