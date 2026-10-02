# Colab and cognitive agents (learning notes)

Status: NOTES from one web search on 2026-10-01; nothing here was run on Colab. The owner wrote "colab" and "cognitive agent" briefly; I read the first as Google Colab and the second as an agent with a memory and a reflect loop. Correct me if either is wrong.

## What Colab is for in this company

Colab rents a cloud GPU in a notebook. For PMCR-O the useful job is the one in the owner's first seed ("PMCRO fine-tunes PMCRO"): take a small open model, fine-tune it cheaply with LoRA or QLoRA, then export it to run locally in Ollama. Reported by the sources below: a free T4 GPU handles roughly 1B to 10B parameter models; QLoRA with Unsloth needs about 6 GB of VRAM for a 7 to 8B model; the free tier's roughly 12.7 GB of CPU RAM can crash when merging adapters into the base model; very large models do not fit. Treat these as approximate and re-check before relying on them.

## Rules for using it here

- Colab is Google's cloud. Anything uploaded leaves the owner's machine. Only data cleared for training may go there: public-tier material, and frames from cycles with `executed: true` and `checker_independent: true` that the founder has accepted (ADR 0013, `product/trail.md`). Never the private or roundtable tiers, memory, the account registry or credentials.
- No secrets in notebooks. A notebook is readable by whoever can open it; pass nothing sensitive and never paste keys.
- Runtimes are temporary and disconnect. Keep checkpoints, save adapters off the runtime, and record each run as a trail frame with its cost and the exact data hash.
- A notebook is an artifact like a skill: store it as an asset of a skill, with a README saying what it does and was not tested on.
- The offline i9 can do the same fine-tune locally if it has enough GPU memory, with no upload (`docs/offline-kit.md`); Colab is for when it does not.

## Cognitive agents, in the company's terms

A cognitive agent here is the loop the company already has, plus memory: perceive (inbox, capture), recall (shared memory, ADR 0021), plan, act through bounded skills, get independently checked, reflect, and write a candidate lesson back to memory for the founder to accept. The pieces exist as separate plugins; nothing yet wires them into one agent. The PMCR-O-Marketplace repo lists a `cognitive-trails` specialty skill that I have not read.

## Next steps (not built)

A notebook template for LoRA fine-tuning with a data-eligibility check up front; a trail-frame template for a training run; a comparison of the fine-tuned model against the base model on held-out evaluation sets that are never trained on.

## Sources

- [Fine-Tuning a Large Language Model on Google Colab (Free GPU), a practical guide](https://medium.com/@amrilsyaifa_21001/fine-tuning-a-large-language-model-on-google-colab-free-gpu-a-practical-guide-3f7f5d5c444f)
- [Fine-Tune SLMs for Free: From Google Colab to Ollama (DZone)](https://dzone.com/articles/fine-tune-lms-for-free)
- [GPU VRAM requirements to fine-tune LLMs in 2026](https://www.spheron.network/blog/gpu-vram-requirements-fine-tune-llm-2026/)
- [Fine-tune Gemma in Keras using LoRA (Google)](https://ai.google.dev/gemma/docs/core/lora_tuning)
