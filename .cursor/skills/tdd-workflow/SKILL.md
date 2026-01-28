---
name: tdd-workflow
description: Use this skill when writing new features, fixing bugs, or refactoring code. Enforces language/toolchain agnostic TDD with meaningful coverage (unit + integration + E2E when applicable).
---

# Test-Driven Development Workflow

This skill enforces test-first development regardless of language/framework/toolchain.

**Do NOT assume npm/Jest/Playwright.** Use the repository’s existing test runner, conventions, and tooling.

## When to Activate

- Writing new features or functionality
- Fixing bugs or issues
- Refactoring existing code
- Adding API endpoints / public interfaces
- Creating new UI/components

## Core Principles

### 1) Tests BEFORE Code

Always write tests first, then implement the minimal code to make tests pass.

### 2) Coverage Requirements

- Target **80%+** coverage when the project supports coverage tooling
- Always cover:
  - Happy paths
  - Failure paths
  - Boundary conditions (0/min/max/±1, empty/NULL where meaningful)
- If coverage tooling is not available, compensate with additional branch/edge tests

### 3) Test Types (pick what fits the repo)

- **Unit tests**: pure logic, fast, isolated
- **Integration tests**: DB/network/IO flows, API endpoints, service interactions
- **E2E tests**: critical user flows (only if the repo already uses E2E tooling)

## Mandatory Workflow (Red → Green → Refactor)

### Step 1: Write the user journey / behavior

```text
As a [role], I want to [action], so that [benefit]
```

### Step 2: Generate test cases

For each behavior, design:
- normal/happy path
- failure paths
- boundary cases

### Step 3: RED — write failing test(s)

Write the smallest test that demonstrates the missing behavior.

### Step 4: Verify RED — run the smallest relevant tests (must fail)

```bash
# Pick the smallest relevant scope that covers the change, e.g.:
# pytest path/to/test_file.py -q
# go test ./... -run TestName
# cargo test test_name
# mvn -Dtest=SomeTest test
# dotnet test --filter FullyQualifiedName~TestName
# npm test -- path/to/test (only if repo uses it)
```

### Step 5: GREEN — implement minimal code

Do the least work to make the test pass. No extra features.

### Step 6: Verify GREEN — rerun the same tests (must pass)

Run the same smallest scope again. Only expand to full suite if needed.

### Step 7: REFACTOR — improve design with tests green

- Remove duplication
- Improve naming
- Reduce nesting
- Improve error handling

### Step 8: Coverage (if supported)

```bash
# Examples (use only what exists in the repo):
# pytest --cov
# go test -cover ./...
# dotnet test /p:CollectCoverage=true
# npm test -- --coverage
```

## Minimal Test Templates (pseudocode)

### Unit test

```text
test("does X", () => {
  // Given
  // When
  // Then
})
```

### API integration test

```text
test("GET /resource returns 200 and expected shape", () => {
  // Given: seeded data
  // When: request is made
  // Then: status, body, headers validated
})
```

### E2E test (only if repo uses E2E)

```text
test("user completes critical flow", () => {
  // Navigate → interact → assert visible outcomes
})
```

## Definition of Done (TDD)

- [ ] Every new behavior has tests
- [ ] You watched the tests fail before writing production code
- [ ] Happy + failure + boundary cases covered
- [ ] Tests are deterministic (no flakes)
- [ ] Coverage target met or rationale documented
