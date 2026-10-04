# KnowledgeHub RAG v1.7 Stable

Stable baseline:
- default mode: fast verified extractive response;
- local LLM is explicitly experimental;
- top-3 retrieved evidence is used;
- verified LLM answers require Ukrainian quality >= 85;
- v1.6 malformed Ukrainian forms are covered by regression tests.

This version is intended as the baseline for further development.
Faster local inference (GGUF/llama.cpp/GPU) should be added later as a separate measured stage.
