from __future__ import annotations

from fastapi.testclient import TestClient

from app.main import app

REQUIRED_KEYS = {
    "title",
    "goals",
    "success_metrics",
    "user_stories",
    "acceptance_criteria",
    "technical_requirements",
    "non_functional_requirements",
    "risk_register",
    "assumptions",
    "clarification_questions",
}

TEST_INPUTS = [
    {"input_type": "text", "input_text": "Build an AI assistant that summarizes customer calls and suggests follow-up tasks."},
    {"input_type": "slack_proposal", "input_text": "Proposal: launch internal bot for sprint planning; include Jira sync and edge case handling."},
    {"input_type": "feature_brief", "input_text": "Feature brief: automate release notes from merged PRs and notify stakeholders."},
    {"input_type": "text", "input_text": "Need a policy engine for human approvals when tests fail in deployment pipelines."},
    {"input_type": "feature_brief", "input_text": "Create a roadmap assistant that drafts epics, stories, assumptions, and risks."},
    {"input_type": "text", "input_text": "Design an onboarding flow analyzer to catch drop-offs and propose experiments."},
]


def validate_shape(payload: dict) -> tuple[bool, str]:
    prd = payload["execution_pack"]["structured_prd"]
    keys = set(prd.keys())
    if keys != REQUIRED_KEYS:
        return False, f"Invalid key set: {keys}"
    for key in REQUIRED_KEYS - {"title"}:
        if not isinstance(prd[key], list) or not prd[key]:
            return False, f"Field {key} empty or non-list"
    if not isinstance(prd["title"], str) or not prd["title"].strip():
        return False, "title missing"
    return True, "shape valid"


def main() -> None:
    client = TestClient(app)
    results = []

    for i, test_input in enumerate(TEST_INPUTS, start=1):
        response = client.post("/generate-pack", json=test_input)
        if response.status_code != 200:
            results.append((i, False, f"status {response.status_code}"))
            continue
        ok, message = validate_shape(response.json())
        results.append((i, ok, message))

    print("=== Automated API Shape Test Results ===")
    pass_count = 0
    for idx, ok, msg in results:
        status = "PASS" if ok else "FAIL"
        pass_count += int(ok)
        print(f"Test {idx}: {status} - {msg}")

    print(f"Summary: {pass_count}/{len(results)} passed")
    if pass_count != len(results):
        raise SystemExit(1)

    ux_payload = {
        "input_type": "text",
        "input_text": "Build an AI copilot for roadmap planning and delivery decisions.",
        "edge_case_inputs": ["missing dependency owners", "unclear rollback policy"],
        "decision_notes": "Prioritize safe rollout over speed.",
    }
    ux_response = client.post("/ux-flow", json=ux_payload)
    if ux_response.status_code != 200:
        print(f"UX Flow: FAIL - status {ux_response.status_code}")
        raise SystemExit(1)
    ux_json = ux_response.json()
    required_ux_keys = {
        "stage",
        "execution_pack",
        "missed_edge_cases_prompt",
        "assumptions_made",
        "prd_tests",
        "action_required",
        "decision_options",
        "message_to_user",
    }
    if set(ux_json.keys()) != required_ux_keys:
        print("UX Flow: FAIL - invalid response keys")
        raise SystemExit(1)
    print("UX Flow: PASS - endpoint returns full interactive decision payload")


if __name__ == "__main__":
    main()
