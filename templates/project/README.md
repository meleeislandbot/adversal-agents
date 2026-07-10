# Adversal project template

This directory contains files that belong in an instantiated Adversal project root.

Copy the contents of this directory into the target project root when the setup instructions decide that the project-local harness structure should be bootstrapped from template assets.

Do not treat this template directory as active runtime state for the source repository.

## Contents

```text
.adversal/      # ledgers, scenario seeds, templates, worker status/catalog
roles/           # isolated council role prompts
scripts/        # optional project-local helpers
llm-wiki/        # empty gated canonical knowledge base
docs/            # copied epistemic and operating contracts
lean-toolchain   # pinned Lean release
lakefile.toml    # matching pinned mathlib release
```

The deterministic bootstrap also installs these runtime context files:

```text
.hermes.md
AGENTS.md
CLAUDE.md
GEMINI.md
```

Do not copy files manually over an existing project. Use
`scripts/bootstrap_adversal.py`; it checks conflicts before writing and records
the exact source commit under `.adversal/bootstrap/`.
