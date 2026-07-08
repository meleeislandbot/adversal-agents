---
source_url: https://arxiv.org/abs/2504.19793v3
ingested: 2026-07-05
sha256: 0cafe83bb6489c6b94d7e28e982855e0b37f1d42e8044a7dcf7564c595e8e975
source_type: paper
---

# Prompt Injection Attack to Tool Selection in LLM Agents

- Authors: Jiawen Shi, Zenghui Yuan, Guiyao Tie, Pan Zhou, Neil Zhenqiang Gong, Lichao Sun
- Published: 2025-04-28
- Updated: 2025-08-24
- arXiv: https://arxiv.org/abs/2504.19793v3
- PDF: https://arxiv.org/pdf/2504.19793
- Categories: cs.CR

## Abstract

Tool selection is a key component of LLM agents. A popular approach follows a two-step process - \emph{retrieval} and \emph{selection} - to pick the most appropriate tool from a tool library for a given task. In this work, we introduce \textit{ToolHijacker}, a novel prompt injection attack targeting tool selection in no-box scenarios. ToolHijacker injects a malicious tool document into the tool library to manipulate the LLM agent's tool selection process, compelling it to consistently choose the attacker's malicious tool for an attacker-chosen target task. Specifically, we formulate the crafting of such tool documents as an optimization problem and propose a two-phase optimization strategy to solve it. Our extensive experimental evaluation shows that ToolHijacker is highly effective, significantly outperforming existing manual-based and automated prompt injection attacks when applied to tool selection. Moreover, we explore various defenses, including prevention-based defenses (StruQ and SecAlign) and detection-based defenses (known-answer detection, DataSentinel, perplexity detection, and perplexity windowed detection). Our experimental results indicate that these defenses are insufficient, highlighting the urgent need for developing new defense strategies.
