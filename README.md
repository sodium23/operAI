# AI Execution Operating System Backend Prototype (FastAPI)

This Replit-ready backend prototype implements an **AI Execution OS** flow:
- give an idea
- generate detailed PM stories as structured PRD JSON
- call out assumptions and missed edge cases
- run PRD-derived tests and surface failures for user decisions
- refine prompts iteratively until stable confidence

It uses **Claude as the primary LLM** via an abstraction that supports either real API calls or mock mode.

## Quoted UX state
- "FastAPI backend running"
- "Claude (primary) connected"
- "PM Agent generating structured JSON"
- "5+ tested inputs"
- "Prompt refined until stable"

## Architecture

Modular components under `app/`:
- `clients/claude_client.py`: Claude adapter (real + mock mode)
- `services/intent_parser.py`: Step 1 intent parsing
- `services/prompt_builder.py`: Step 2 prompt construction
- `services/result_parser.py`: Step 3 result parsing into strict schema
- `agents/evaluation_engine.py`: completeness/risk/hallucination metrics
- `agents/governance_logger.py`: prompt/model/usage/PII logs
- `agents/finance_agent.py`: token-cost estimation stub
- `agents/pm_agent.py`: orchestrates multi-step PM workflow and PRD-derived tests
- `main.py`: FastAPI endpoints

Designed for future agents like Architecture, Security, and Critique.

## API Endpoints

- `GET /health`
  - returns backend and Claude connectivity mode status.

- `POST /generate-pack`
  - input: `{ "input_text": "...", "input_type": "text|slack_proposal|feature_brief" }`
  - output: structured PRD + execution pack with:
    - parsed intent
    - prompt used
    - evaluation scores
    - governance metadata
    - finance estimate

- `POST /refine-until-stable`
  - input: generate-pack payload + optional:
    - `stability_threshold` (default from env)
    - `max_iterations` (default from env)
  - iteratively refines prompt until confidence threshold is reached.

- `POST /run-prd-tests`
  - generates a PRD and executes mock PRD-derived test checks.
  - if failures occur, response guidance asks for user inputs/decisions.

- `POST /ux-flow`
  - purpose-built UX flow endpoint:
    1. give an idea
    2. generate detailed PM stories (structured PRD)
    3. ask for missed edge cases and show assumptions made
    4. run PRD-derived tests
    5. if failures occur, return `action_required=true` and decision options for user input
  - accepts optional `edge_case_inputs` and `decision_notes` for follow-up turns.

## Environment Variables

Create `.env` (optional):

```bash
CLAUDE_API_KEY=your_key_here
CLAUDE_MODEL=claude-3-5-sonnet-20241022
MOCK_LLM=true
STABILITY_THRESHOLD=0.9
MAX_REFINEMENT_ITERATIONS=5
GOVERNANCE_LOG_PATH=governance.log
TOKEN_COST_PER_1K=0.02
```

### Claude usage mode
- `MOCK_LLM=true` or empty `CLAUDE_API_KEY` -> mock output.
- `MOCK_LLM=false` + valid `CLAUDE_API_KEY` -> real Anthropic API call.

## Run Locally / Replit

```bash
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## Automated Tests (5+ inputs)

Script posts 6 sample inputs to `/generate-pack` and validates output JSON shape.

```bash
python scripts/test_api.py
```

## Replacing Mock with Real Claude Client

1. Set `MOCK_LLM=false`.
2. Provide `CLAUDE_API_KEY` in environment.
3. Ensure Anthropic API network access is available.
4. Optional: harden parsing with stricter JSON extraction and retry strategy.

## Governance & Finance Notes

- Governance logger writes JSONL entries with:
  - prompt
  - model
  - estimated token usage
  - simple PII email flag
- Finance Agent computes mock cost: `(tokens / 1000) * TOKEN_COST_PER_1K`.


## PR Creation Troubleshooting

If PR creation fails in a fresh environment, run:

```bash
python scripts/pr_diagnostics.py
```

Common causes:
- No git remote configured (`git remote add origin <repo-url>`)
- Branch not pushed with upstream (`git push -u origin <branch>`)

Note: the local `make_pr` tool records PR title/body metadata for automation, but a real GitHub PR still requires a valid remote + pushed branch.
