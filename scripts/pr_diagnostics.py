from __future__ import annotations

import subprocess
import sys


def run(cmd: list[str]) -> str:
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        return ""
    return result.stdout.strip()


def main() -> None:
    branch = run(["git", "rev-parse", "--abbrev-ref", "HEAD"])
    remotes = run(["git", "remote", "-v"])
    upstream = run(["git", "rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{u}"])

    print("=== PR Diagnostics ===")
    print(f"Current branch: {branch or 'unknown'}")

    if not remotes:
        print("FAIL: No git remote configured. Add an origin remote before creating a real GitHub PR.")
        print("Hint: git remote add origin <repo-url>")
        sys.exit(1)

    print("Remotes:")
    print(remotes)

    if not upstream:
        print("WARN: Branch has no upstream tracking branch.")
        print(f"Hint: git push -u origin {branch}")
        sys.exit(2)

    print(f"Upstream: {upstream}")
    print("PASS: Repo has remote + upstream branch configured for PR creation.")


if __name__ == "__main__":
    main()
