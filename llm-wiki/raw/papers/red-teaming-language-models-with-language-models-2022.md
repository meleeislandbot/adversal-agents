---
source_url: https://arxiv.org/abs/2202.03286v1
ingested: 2026-07-05
sha256: 6697b3bcb58abea2848269dc9c6c0d9503cf4e0a10a8227c409ad7bface8afae
source_type: paper
---

# Red Teaming Language Models with Language Models

- Authors: Ethan Perez, Saffron Huang, Francis Song, Trevor Cai, Roman Ring, John Aslanides, Amelia Glaese, Nat McAleese, Geoffrey Irving
- Published: 2022-02-07
- Updated: 2022-02-07
- arXiv: https://arxiv.org/abs/2202.03286v1
- PDF: https://arxiv.org/pdf/2202.03286
- Categories: cs.CL, cs.AI, cs.CR, cs.LG

## Abstract

Language Models (LMs) often cannot be deployed because of their potential to harm users in hard-to-predict ways. Prior work identifies harmful behaviors before deployment by using human annotators to hand-write test cases. However, human annotation is expensive, limiting the number and diversity of test cases. In this work, we automatically find cases where a target LM behaves in a harmful way, by generating test cases ("red teaming") using another LM. We evaluate the target LM's replies to generated test questions using a classifier trained to detect offensive content, uncovering tens of thousands of offensive replies in a 280B parameter LM chatbot. We explore several methods, from zero-shot generation to reinforcement learning, for generating test cases with varying levels of diversity and difficulty. Furthermore, we use prompt engineering to control LM-generated test cases to uncover a variety of other harms, automatically finding groups of people that the chatbot discusses in offensive ways, personal and hospital phone numbers generated as the chatbot's own contact info, leakage of private training data in generated text, and harms that occur over the course of a conversation. Overall, LM-based red teaming is one promising tool (among many needed) for finding and fixing diverse, undesirable LM behaviors before impacting users.
