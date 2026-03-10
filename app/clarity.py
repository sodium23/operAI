def clarity_score(text: str):
    score = 0
    text = text.lower()

    if any(x in text for x in ["for", "who"]):
        score += 1
    if any(x in text for x in ["b2b", "b2c"]):
        score += 1
    if any(x in text for x in ["web", "mobile", "app", "api"]):
        score += 1
    if any(x in text for x in ["subscription", "monetize", "pay"]):
        score += 1
    if len(text.split()) > 12:
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
