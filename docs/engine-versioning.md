# Engine Versioning


The engine versioning is a key component of the BudConnect service. It is responsible for storing the engine versions, model compatibilities, and other engine related resources.

For the vllm engine, the build will be done from the forked version of the vllm repo with required changes to support the bud stack. The versioning will not be same as the vllm repo. But the versoning will be done based on the releases of Bud. 

The engine versions will be pushed to budstudio docker hub with respective tags.

| Device Architecture | Image Name | Version |
| ------------------- | ---------- | ------- |
| cuda                | budstudio/vllm-cuda | 0.9.0   |
| cpu                 | budstudio/vllm-cpu | 0.9.0   |
| rocm                | budstudio/vllm-rocm | —       |
| hpu                 | budstudio/vllm-hpu | —       |

> Versions track Bud releases, not upstream vLLM. `0.9.0` was built from the vLLM fork at upstream commit `481e481be`. ROCM/HPU images are not currently published. When bumping the version, refresh the vLLM-derived data in the same pass: `budconnect/seeders/data/engines.json` (architecture lists + `container_image`), `budconnect/seeders/data/model_architectures.json`, the `_VLLM_MODELS` mirror in `scripts/arch_support_to_seeder.py`, and the hardcoded parser menus in `budconnect/seeders/engine.py`.

### Architecture support policy

The `0.9.0` compatibility list has **363** architectures = **354 natively supported** (vLLM's `_VLLM_MODELS` registry union) **+ 9 served via vLLM's Transformers backend**.

BudConnect is a pre-deployment compatibility oracle, so an architecture stays listed as long as the engine can *deploy* it — natively **or** via the Transformers backend (which vLLM's default `--model-impl auto` uses automatically, per `_try_resolve_transformers` in `registry.py`). The authoritative per-arch test is HF Transformers' `getattr(transformers, ArchName).is_backend_compatible()`; it was run against `transformers==5.13.1` (the vLLM 0.9.0 pin).

- **Kept via Transformers backend (9):** `AyaVisionForConditionalGeneration`, `Dots1ForCausalLM`, `ErnieModel`, `ErnieForSequenceClassification`, `ErnieForTokenClassification`, `FuyuForCausalLM`, `MiniMaxForCausalLM`, `MusicFlamingoForConditionalGeneration`, `PersimmonForCausalLM`.
- **Removed (20)** — vLLM dropped native support (`_PREVIOUSLY_SUPPORTED_MODELS`) **and** the Transformers backend cannot serve them: no HF class (`Grok1*`, `QWenLMHeadModel`, `QwenVLForConditionalGeneration`, `Baichuan*`, `JAISLMHeadModel`, `MantisForConditionalGeneration`, `MiniMaxM1/Text01/VL01`), backend-incompatible (`BambaForCausalLM`), Transformers-v4-locked (`Tarsier*`), or Llama-family aliases whose real checkpoints already declare the still-supported successor arch (`InternLM*`, `Aquila*`, `XverseForCausalLM`, `TeleChatForCausalLM` → `LlamaForCausalLM`/`TeleChat2ForCausalLM`).

Note: `scripts/arch_support_to_seeder.py` mirrors only vLLM's **native** registry (354); the 9 Transformers-backend entries are maintained on top of that in `engines.json` + `model_architectures.json`, so those files are intentionally a superset of the mirror.
