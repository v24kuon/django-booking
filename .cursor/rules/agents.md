# Agent Orchestration

## Available Agents

Located in `.cursor/agents/` (this repo):

| Agent | Purpose | When to Use |
|-------|---------|-------------|
| planner | Implementation planning | Complex features, refactoring, ambiguous requirements |
| architect | System design | Architectural decisions, scalability, boundaries |
| tdd-guide | Test-driven development | New features, bug fixes, risky refactors |
| test-runner | Run/repair tests | When tests fail or you need the smallest relevant suite |
| code-reviewer | Code review | After meaningful code changes |
| code-simplifier | Simplify code | Reduce complexity, improve readability without behavior change |
| security-reviewer | Security analysis | Auth/input/payment/secrets, external integrations |
| refactor-cleaner | Dead code cleanup | Removing unused code safely |
| doc-updater | Documentation & codemaps | Updating docs from current code |
| verifier | Skeptical validation | Confirm changes actually work |

## Immediate Agent Usage

No user prompt needed:
1. Complex feature requests - Use **planner** agent
2. Code just written/modified - Use **code-reviewer** agent
3. Bug fix or new feature - Use **tdd-guide** agent
4. Architectural decision - Use **architect** agent

## Parallel Task Execution

ALWAYS use parallel Task execution for independent operations:

```markdown
# GOOD: Parallel execution
Launch 3 agents in parallel:
1. Agent 1: Security analysis of authentication/authorization changes
2. Agent 2: Performance review of the hot path (cache/DB/API)
3. Agent 3: Run language-appropriate static checks for touched files (lint/type-check/build)

# BAD: Sequential when unnecessary
First agent 1, then agent 2, then agent 3
```

## Multi-Perspective Analysis

For complex problems, use split role sub-agents:
- Factual reviewer
- Senior engineer
- Security expert
- Consistency reviewer
- Redundancy checker
