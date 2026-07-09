# Adversal project template

This directory contains files that belong in an instantiated Adversal project root.

Copy the contents of this directory into the target project root when the setup instructions decide that the project-local harness structure should be bootstrapped from template assets.

Do not treat this template directory as active runtime state for the source repository.

## Contents

```text
.adversal/      # ledgers, scenario seeds, templates, worker status/catalog
scripts/        # optional project-local helpers
```

After copying, the target project root should also contain the harness context files:

```text
.hermes.md
AGENTS.md
CLAUDE.md
GEMINI.md
```
