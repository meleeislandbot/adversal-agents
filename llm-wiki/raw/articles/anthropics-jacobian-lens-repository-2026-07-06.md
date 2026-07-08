---
source_url: https://github.com/anthropics/jacobian-lens
ingested: 2026-07-06
sha256: 3cf86920e479c5d389ce7775079475401cab9cb1faa7d01e5b9a4ec737576ac1
source_type: repository
---

# anthropics/jacobian-lens repository

Source inspected: `https://github.com/anthropics/jacobian-lens` and README on 2026-07-06.

Repository metadata from GitHub API:

- Full name: `anthropics/jacobian-lens`
- Description: `Companion code for the global workspace interpretability paper`
- License from README: Apache License 2.0.
- README warning: reference implementation; not maintained and not accepting contributions.

README summary:

- Implements the Jacobian lens for open-weight decoder transformers.
- The lens reads out what an internal activation is disposed to make the model say.
- It linearly transports a residual-stream vector at a layer/position into the final-layer basis, then decodes with the model's unembedding.
- Formula in README: `lens_l(h) = unembed( J_l @ h ), J_l = E[∂h_final / ∂h_l]`.
- Examples use Qwen, and other HuggingFace decoder models are expected to adapt cleanly.
- The paper's lenses used 1000 sequences of 128 tokens from a pretraining-like corpus; README says quality saturates quickly and ~100 prompts is usable.
- Fitting time is dominated by the model's backward pass; parallelization can fit on slices and merge.

Implication: usable as future reference for a local/open-model interpretability worker, but not directly usable on closed provider CLI workers because it requires model internals/activations.
