# Engine Versioning


The engine versioning is a key component of the BudConnect service. It is responsible for storing the engine versions, model compatibilities, and other engine related resources.

For the vllm engine, the build will be done from the forked version of the vllm repo with required changes to support the bud stack. The versioning will not be same as the vllm repo. But the versoning will be done based on the releases of Bud. 

The engine images are published with version tags under `registry.bud.studio/runtime`; the image per device is listed below.

| Device Architecture | Image Name | Version |
| ------------------- | ---------- | ------- |
| cuda                | registry.bud.studio/runtime/vllm-cuda | 0.10.0  |
| cpu                 | registry.bud.studio/runtime/vllm-cpu | 0.10.0  |
| rocm                | registry.bud.studio/runtime/vllm-rocm | —       |
| hpu                 | registry.bud.studio/runtime/vllm-hpu | —       |

> Versions track Bud releases, not upstream vLLM, and each device build has its own version lineage. `0.10.0` (CUDA and CPU) is upstream vLLM `v0.31.0` (commit `db9527a46`); the CUDA image is labelled `vllm/vllm-openai:v0.31.0` and the CPU image reports `vllm 0.31.0+cpu` with `transformers 5.17.0`. The previous builds were CUDA `0.9.0` / CPU `0.6.0` (fork at upstream `481e481be`). ROCM/HPU images are not currently published. When bumping the version, refresh the vLLM-derived data in the same pass: `budconnect/seeders/data/engines.json` (architecture lists + `container_image`), `budconnect/seeders/data/model_architectures.json`, the `_VLLM_MODELS` mirror in `scripts/arch_support_to_seeder.py`, and the hardcoded parser menus in `budconnect/seeders/engine.py`.

### Architecture support policy

The `0.10.0` compatibility list has **397** architectures = **387 natively supported** (vLLM's `_VLLM_MODELS` registry union) **+ 10 served via vLLM's Transformers backend**.

BudConnect is a pre-deployment compatibility oracle, so an architecture stays listed as long as the engine can *deploy* it — natively **or** via the Transformers backend (which vLLM's default `--model-impl auto` uses automatically, per `_try_resolve_transformers` in `registry.py`). The per-arch test is HF Transformers' `getattr(transformers, ArchName).is_backend_compatible()`, run inside the `0.10.0` CPU image (`transformers==5.17.0`). vLLM `v0.31.0` also accepts `_can_set_attn_implementation()`, but BudConnect keeps the stricter `is_backend_compatible()` test because the backend only covers full/sliding attention in encoder-only, decoder-only and MoE models — e.g. `BambaForCausalLM` (hybrid Mamba) passes the looser gate but is not listed.

- **Kept via Transformers backend (10):** `AyaVisionForConditionalGeneration`, `ChameleonForConditionalGeneration`, `Dots1ForCausalLM`, `ErnieModel`, `ErnieForSequenceClassification`, `ErnieForTokenClassification`, `FuyuForCausalLM`, `MiniMaxForCausalLM`, `MusicFlamingoForConditionalGeneration`, `PersimmonForCausalLM`.
- **Removed in `0.10.0` (15)** — vLLM dropped native support and the Transformers backend cannot serve them: no HF class (`ArcticForCausalLM`, `Cheers`, `CheersForConditionalGeneration`, `Fairseq2LlamaForCausalLM`, `FireRedLIDForConditionalGeneration`, `GritLM`, `HCXVisionForCausalLM`, `MPTForCausalLM`, `OuroForCausalLM`, `Plamo2ForCausalLM`, `RWForCausalLM`, `StableLMEpochForCausalLM`), backend-incompatible (`MptForCausalLM`), superseded by the generic `Terratorch` arch (`PrithviGeoSpatialMAE`), or renamed (`ExaoneMoEForCausalLM` → `ExaoneMoeForCausalLM`; `v0.31.0` registers only the new casing).

`supports_lora` / `supports_pipeline_parallelism` in `model_architectures.json` come from vLLM's own `supports_lora()` / `supports_pp()` on the class the CUDA image loads (for the per-device `vllm.models.*` packages, the `nvidia/` implementation). The CPU build swaps in CPU variants for DeepSeek-V4: `DeepseekV4ForCausalLM` has no LoRA there and `DeepseekV4ForConditionalGeneration` is a stub that raises `NotImplementedError`.

Note: `scripts/arch_support_to_seeder.py` mirrors only vLLM's **native** registry (387); the 10 Transformers-backend entries are maintained on top of that in `engines.json` + `model_architectures.json`, so those files are intentionally a superset of the mirror.
