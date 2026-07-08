# Wiki Schema

## Domain

This wiki covers the **Adversal Agents** project: research, design, evidence, prior art, implementation decisions, and evaluation methods for adversarial multi-agent AI systems that verify AI-generated work.

The wiki is project-local. It should help future agents and humans understand what has been researched, what is established, what remains uncertain, and which design decisions are grounded in evidence.

## Core principles

- Raw sources are immutable after ingestion.
- Separate **facts**, **inferences**, **speculation**, and **open questions**.
- Prefer primary sources: papers, official docs, standards, repositories, benchmarks, datasets, source code, and original announcements.
- Do not treat LLM consensus as evidence by itself.
- Preserve disagreement and minority evidence when relevant.
- Every substantial claim should trace back to a source.
- Every meaningful wiki action updates `index.md` and appends to `log.md`.

## Directory structure

```text
llm-wiki/
├── SCHEMA.md
├── index.md
├── log.md
├── raw/
│   ├── articles/
│   ├── papers/
│   ├── discussions/
│   ├── transcripts/
│   └── assets/
├── entities/
├── concepts/
├── comparisons/
├── queries/
├── _meta/
└── _archive/
```

## File names

- Lowercase kebab-case: `multi-agent-debate.md`.
- No spaces in filenames.
- Use Obsidian wikilinks: `[[multi-agent-debate]]`.
- Raw source filenames should include enough context to identify the source and year when useful.

## Frontmatter for wiki pages

Every generated wiki page must start with:

```yaml
---
title: Page Title
created: YYYY-MM-DD
updated: YYYY-MM-DD
type: entity | concept | comparison | query | summary
tags: [tag-one, tag-two]
sources: [raw/papers/example.md]
confidence: high | medium | low
contested: false
contradictions: []
---
```

## Raw source frontmatter

Raw sources should include:

```yaml
---
source_url: https://example.com/source
ingested: YYYY-MM-DD
sha256: <sha256 of body after frontmatter>
source_type: paper | article | docs | discussion | transcript | repository | dataset | other
---
```

Compute `sha256` over the body only, after the closing frontmatter block.

## Tag taxonomy

Allowed tags:

- `adversal-agents`
- `research`
- `prior-art`
- `red-teaming`
- `multi-agent`
- `agentic-ai`
- `llm-evaluation`
- `hallucination`
- `verification`
- `evidence`
- `provenance`
- `debate`
- `consensus`
- `comparison`
- `tool-use`
- `memory`
- `security`
- `safety`
- `benchmark`
- `implementation`
- `architecture`
- `risk`
- `open-question`
- `interpretability`
- `alignment`

Add new tags here before using them.

## Page thresholds

Create a page when:

- a concept, paper, framework, benchmark, or actor is central to the project;
- it appears across 2+ relevant sources;
- it captures a reusable design decision;
- it would be painful to reconstruct from chat history.

Do not create pages for passing mentions.

Split pages when they exceed roughly 200 lines or combine multiple separable concepts.

## Evidence labels

Use these labels inside pages when helpful:

- **Facts:** directly supported by cited sources.
- **Inferences:** synthesis from the evidence, not directly stated.
- **Speculation:** plausible but weakly established.
- **Open questions:** unresolved decisions or missing evidence.
- **Design implication:** what this means for Adversal Agents.

## Update policy

When new information conflicts with existing content:

1. Do not silently overwrite.
2. Add both claims with dates and sources.
3. Mark `contested: true` if the contradiction matters.
4. Add affected pages to `contradictions:`.
5. Surface the conflict in the next synthesis or lint report.

## Lint policy

Periodic lint should check:

- broken wikilinks;
- orphan pages;
- pages missing from `index.md`;
- missing or invalid frontmatter;
- tags not in taxonomy;
- low-confidence pages;
- contested pages;
- raw source sha256 drift;
- pages over 200 lines;
- stale claims or pages with weak provenance.
