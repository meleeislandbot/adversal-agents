---
source_url: https://arxiv.org/abs/2505.05849v4
ingested: 2026-07-05
sha256: 0b2fdcca0d67aa7ba25573934b591584c93049ad4c08d7bc2de61bc25d934195
source_type: paper
---

# AgentVigil: Generic Black-Box Red-teaming for Indirect Prompt Injection against LLM Agents

- Authors: Zhun Wang, Vincent Siu, Zhe Ye, Tianneng Shi, Yuzhou Nie, Xuandong Zhao, Chenguang Wang, Wenbo Guo, Dawn Song
- Published: 2025-05-09
- Updated: 2025-06-14
- arXiv: https://arxiv.org/abs/2505.05849v4
- PDF: https://arxiv.org/pdf/2505.05849
- Categories: cs.CR, cs.AI

## Abstract

The strong planning and reasoning capabilities of Large Language Models (LLMs) have fostered the development of agent-based systems capable of leveraging external tools and interacting with increasingly complex environments. However, these powerful features also introduce a critical security risk: indirect prompt injection, a sophisticated attack vector that compromises the core of these agents, the LLM, by manipulating contextual information rather than direct user prompts. In this work, we propose a generic black-box fuzzing framework, AgentVigil, designed to automatically discover and exploit indirect prompt injection vulnerabilities across diverse LLM agents. Our approach starts by constructing a high-quality initial seed corpus, then employs a seed selection algorithm based on Monte Carlo Tree Search (MCTS) to iteratively refine inputs, thereby maximizing the likelihood of uncovering agent weaknesses. We evaluate AgentVigil on two public benchmarks, AgentDojo and VWA-adv, where it achieves 71% and 70% success rates against agents based on o3-mini and GPT-4o, respectively, nearly doubling the performance of baseline attacks. Moreover, AgentVigil exhibits strong transferability across unseen tasks and internal LLMs, as well as promising results against defenses. Beyond benchmark evaluations, we apply our attacks in real-world environments, successfully misleading agents to navigate to arbitrary URLs, including malicious sites.
