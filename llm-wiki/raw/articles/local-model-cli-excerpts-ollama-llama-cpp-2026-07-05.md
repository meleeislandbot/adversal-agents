---
source_url: https://raw.githubusercontent.com/ollama/ollama/main/README.md ; https://raw.githubusercontent.com/ggml-org/llama.cpp/master/README.md
ingested: 2026-07-05
sha256: d1db2da0b036ded42ff8b7a210aa3483c79a3bf8a5c90278e88e1db657d3209e
source_type: docs
---

# Local model CLI excerpts: Ollama and llama.cpp — 2026-07-05

Inspected official repository READMEs. The binaries were not installed locally during inspection.

## Ollama

Official README shows interactive model execution:

```bash
ollama run gemma4
```

It also exposes a REST API at localhost. For one-shot automation, the non-streaming API shape is useful:

```bash
curl http://localhost:11434/api/chat -d '{
  "model": "gemma4",
  "messages": [{"role": "user", "content": "Why is the sky blue?"}],
  "stream": false
}'
```

## llama.cpp

Official README shows local model execution and server mode:

```bash
llama-cli -m my_model.gguf
llama-cli -hf ggml-org/gemma-3-1b-it-GGUF
llama-server -hf ggml-org/gemma-3-1b-it-GGUF
```

llama.cpp emphasizes minimal local inference, Apple Silicon support via Metal/Accelerate, broad CPU support, and quantized GGUF models.

## Design relevance

Local model CLIs are not replacements for frontier reasoning workers, but they are ideal for cheap first-pass mutation, clustering, rough classification, deduplication, and deterministic-ish bulk triage before promoting cases to subscription or paid API workers.
