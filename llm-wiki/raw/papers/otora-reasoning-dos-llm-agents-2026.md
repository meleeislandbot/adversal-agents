---
source_url: https://arxiv.org/abs/2605.08876v2
ingested: 2026-07-05
sha256: ef9c6add23f44fd4ae6ab201d9b9fb2595c66ef1924893bb6defad9dbee9119d
source_type: paper
---

# OTora: A Unified Red Teaming Framework for Reasoning-Level Denial-of-Service in LLM Agents

- Authors: Xinyu Li, Ronghui Mu, Lin Li, Tianjin Huang, Gaojie Jin
- Published: 2026-05-09
- Updated: 2026-06-07
- arXiv: https://arxiv.org/abs/2605.08876v2
- PDF: https://arxiv.org/pdf/2605.08876
- Categories: cs.LG

## Abstract

Large Language Models (LLMs) are increasingly deployed as autonomous agents that execute tool-augmented, multi-step tasks, where latency is a critical factor for real-world applications. Yet an overlooked threat is Reasoning-Level Denial-of-Service (R-DoS), in which an attacker preserves task correctness but degrades availability by inflating an agent's reasoning depth or tool-use budget. We introduce OTora, the first unified, two-stage red-teaming framework for instantiating R-DoS attacks. Stage I optimizes an adversarial trigger that induces targeted tool invocations using insertion-aware scoring and dynamic target co-evolution, supporting both black-box and white-box settings. Stage II generates agent-aware reasoning payloads via an ICL-guided genetic search that amplifies overthinking while maintaining correct task outcomes. Across WebShop, Email, and OS agents built on multiple backbone models such as LLaMA-70B and GPT-OSS-120B, OTora achieves up to 10 times increases in reasoning tokens and order-of-magnitude latency slowdowns, all while preserving near-baseline task accuracy. Finally, we discuss mitigation strategies for detecting and constraining abnormal reasoning and latency spikes. The code is available at https://github.com/llm2409/OTora.
