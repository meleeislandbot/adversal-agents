---
source_url: https://www.anthropic.com/research/global-workspace
ingested: 2026-07-06
sha256: da1cd12f1f1324d357d23ca0d49fe96fab7dfe2f0661c9dfad471ae331f41cf0
source_type: article
---

# Anthropic research page: A global workspace in language models

Source inspected: `https://www.anthropic.com/research/global-workspace`.

Metadata:

- Title: `A global workspace in language models \ Anthropic`
- Description: `Interpretability research on Claude's internal thoughts.`
- Date shown on page: 2026-07-06.
- Linked paper: `http://transformer-circuits.pub/2026/workspace/index.html`
- Linked code: `https://github.com/anthropics/jacobian-lens`
- Linked external commentary PDF: `https://www-cdn.anthropic.com/files/4zrzovbb/website/cc4be2488d65e54a6ed06492f8968398ddc18ebe.pdf`

Key quoted/extracted claims from the page:

- Anthropic says Claude has developed a small collection of internal neural patterns with a special role compared to other processing. They call this collection the **J-space**, named after a Jacobian-based method used to find it.
- Each J-space pattern is linked to a word, but activation does not mean the model is saying that word; it means the word/concept is "on its mind".
- The J-space is described as distinct from explicit scratchpads or chain-of-thought text: it operates silently in internal activations.
- Anthropic claims the J-space can reveal internal thoughts not present in outputs, including examples where models notice bugs, infer protein function from sequence, and flag suspicious search results as prompt injection.
- Reported properties include: reportability, directed modulation, internal reasoning, flexible use across tasks, and selectivity.
- Anthropic frames the philosophical implications as unclear/controversial, but the practical implication as interpretability/auditing: a possible window into model thinking.

Caveat: this is Anthropic's own announcement page. The technical paper is the stronger source for details and limitations.
