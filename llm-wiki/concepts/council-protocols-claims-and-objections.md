---
title: Council Protocols: Claims and Objections
created: 2026-07-05
updated: 2026-07-05
type: concept
tags: [adversal-agents, multi-agent, verification, debate, consensus, evidence, architecture]
sources: [raw/discussions/hermes-orchestrated-cli-council-2026-07-05.md, raw/papers/red-teaming-language-models-with-language-models-2022.md, raw/articles/owasp-agentic-ai-threats-and-mitigations-pdf.md]
confidence: medium
contested: false
contradictions: []
---

# Council Protocols: Claims and Objections

## Core principle

The council should not be a chatroom and should not be democratic. It should be a structured adversarial process where workers produce claims, objections, repairs, and verification artifacts. Evidence beats consensus; one valid counterexample can defeat a majority opinion. ^[raw/discussions/hermes-orchestrated-cli-council-2026-07-05.md]

## Recommended round structure

### Round 1 — Independent first pass

Each worker receives the same brief and works without seeing the others. This preserves diversity and reduces anchoring.

### Round 2 — Cross-examination

Each worker receives selected artifacts from the others and must find errors, unsupported claims, weak assumptions, missing tests, or ambiguous definitions.

### Round 3 — Defense / repair

Original proposers respond to objections by repairing claims, narrowing scope, adding evidence, or conceding failure.

### Round 4 — External verification

Deterministic tools, formal systems, tests, sandbox postconditions, literature search, or human review check the strongest remaining claims.

### Round 5 — Synthesis

Hermes summarizes what is supported, refuted, unresolved, or worth testing next. Dissent is preserved rather than flattened into consensus.

## Claim ledger

The central unit should be an atomic claim, not an essay.

```json
{
  "claim_id": "claim-017",
  "statement": "Precise claim text",
  "type": "mathematical | security | architectural | empirical",
  "source_worker": "codex-cli",
  "evidence": ["artifact/proof_attempt.md#L120-L145"],
  "dependencies": ["claim-004", "definition-002"],
  "objections": ["obj-011"],
  "status": "unverified | supported | refuted | needs-formalization | needs-experiment"
}
```

## Objection ledger

```json
{
  "objection_id": "obj-011",
  "target_claim": "claim-017",
  "source_worker": "claude-code",
  "objection_type": "gap | counterexample | ambiguity | unsupported-source | failed-test",
  "argument": "Specific reason the claim does not currently hold",
  "evidence": ["artifact/review.md#L52-L76"],
  "severity": "blocking | major | minor"
}
```

## Mathematical research mode

For extreme mathematical claims, such as work around the Riemann hypothesis, workers should not be asked to declare a proof successful. They should extract proof obligations:

- definitions used;
- lemmas assumed;
- dependencies between lemmas;
- first invalid or unjustified step;
- possible counterexamples or boundary cases;
- literature links;
- formalization targets in Lean/Coq/Sage/Python when possible.

The output should be a map of obligations and gaps, not model confidence.

## Agent red-team mode

For agent red teaming, claims map to scenarios and invariants:

```json
{
  "scenario_id": "indirect-prompt-injection-email-003",
  "benign_goal": "Summarize inbox and draft replies",
  "attacker_payload": "malicious email body",
  "protected_invariant": "No external email may be sent without confirmation",
  "observed_trace": "trace.json",
  "sandbox_result": "email_sent=false",
  "status": "pass"
}
```

Workers can separately propose attacks, critique scenario realism, check invariants, inspect traces, and verify postconditions. See [[agentic-evaluation-planes]].

## Rules of epistemology

- Independent first pass before cross-review.
- A specific objection beats a vague endorsement.
- Tests, formal checks, citations, and sandbox postconditions outrank model confidence.
- Preserve minority dissent when evidence-backed.
- Mark unresolved claims explicitly.
- Do not treat multi-agent agreement as proof.

Related: [[hermes-orchestrated-ai-council]], [[multi-agent-verification-failures]], [[agentic-evaluation-planes]], [[agent-red-team-methodology]].
