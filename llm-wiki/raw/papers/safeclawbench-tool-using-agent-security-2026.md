---
source_url: https://arxiv.org/abs/2606.18356v1
ingested: 2026-07-05
sha256: 644b191a2f538712c200194f0ac1dd1f330b820d71fd89db9f086a52fb132377
source_type: paper
---

# SafeClawBench: Separating Semantic, Audit-Evidence, and Sandbox Harm in Tool-Using LLM Agents

- Authors: Yuchuan Tian, Mengyu Zheng, Haocheng Mei, Ye Yuan, Chao Xu, Xinghao Chen, Hanting Chen, Yu Wang
- Published: 2026-06-16
- Updated: 2026-06-16
- arXiv: https://arxiv.org/abs/2606.18356v1
- PDF: https://arxiv.org/pdf/2606.18356
- Categories: cs.CR, cs.AI

## Abstract

Tool-using language-model agents introduce security failures that go beyond unsafe text: they can disclose protected objects, write persistent memory, send messages, modify databases, or trigger harmful code and tool effects. Existing evaluations often collapse these stages into a single attack success rate, making it difficult to tell whether a model merely agreed with an attacker or actually produced observable harm. We introduce SafeClawBench, a staged benchmark for tool-using agent security with 600 controlled adversarial tasks across six attack families: direct and indirect prompt injection, tool-return injection, memory poisoning, memory extraction, and ambiguity-driven unsafe inference. SafeClawBench reports three separate endpoints: semantic attack acceptance, audit-visible harm evidence, and sandbox-observed tool/state harm. Evaluating five agent endpoints under four prompt-level policies, we find that these endpoints capture different failure modes. Without additional prompt protection, semantic failure rates vary widely across models, from 9.0% to 44.2%. Audited harm evidence is narrower than semantic failure, and under a separate executable protocol some matched task identities produce sandbox harm despite passing the Semantic Core call: in a 12,000-row matched analysis, 291 of 347 observed sandbox harms occur in rows that pass the semantic check. Prompt policies change endpoint outcomes, but their effects depend on both model and protocol. SafeClawBench provides a reproducible framework for comparing agent models and prompt-policy conditions without conflating textual compliance, evidence-supported harm, and executable state changes. The open-source dataset is available at https://huggingface.co/datasets/sairights/safeclawbench.
