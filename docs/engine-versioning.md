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

> Versions track Bud releases, not upstream vLLM, and each device build has its own version lineage. `0.10.0` (CUDA and CPU) is upstream vLLM `v0.31.0` (commit `db9527a46`); the CUDA image is labelled `vllm/vllm-openai:v0.31.0` and the CPU image reports `vllm 0.31.0+cpu`; both ship `transformers 5.17.0`. The previous builds were CUDA `0.9.0` / CPU `0.6.0` (fork at upstream `481e481be`). ROCM/HPU images are not currently published. When bumping the version, refresh the vLLM-derived data in the same pass: `budconnect/seeders/data/engines.json` (architecture lists, per-version parser lists + `container_image`), `budconnect/seeders/data/model_architectures.json`, and the `_VLLM_MODELS` mirror in `scripts/arch_support_to_seeder.py`.

### Architecture support policy

The `0.10.0` CUDA compatibility list has **397** architectures = **387 natively supported** (vLLM's `_VLLM_MODELS` registry union) **+ 10 served via vLLM's Transformers backend**. The CPU list is the same minus 3 archs the CPU build cannot load (394): `DeepseekV4ForConditionalGeneration` (a CPU stub that raises `NotImplementedError`) and `Dots3NoteForCausalLM` / `Dots3NoteMTPModel` (their import needs CUDA flash-attention).

BudConnect is a pre-deployment compatibility oracle, so an architecture stays listed as long as the engine can *deploy* it — natively **or** via the Transformers backend (which vLLM's default `--model-impl auto` uses automatically, per `_try_resolve_transformers` in `registry.py`). The per-arch test is HF Transformers' `getattr(transformers, ArchName).is_backend_compatible()`, run inside the `0.10.0` CPU image against `transformers==5.17.0`, the version both images ship. vLLM `v0.31.0` also accepts `_can_set_attn_implementation()`, but BudConnect keeps the stricter `is_backend_compatible()` test because the backend only covers full/sliding attention in encoder-only, decoder-only and MoE models — e.g. `BambaForCausalLM` (hybrid Mamba) passes the looser gate but is not listed.

- **Kept via Transformers backend (10):** `AyaVisionForConditionalGeneration`, `ChameleonForConditionalGeneration`, `Dots1ForCausalLM`, `ErnieModel`, `ErnieForSequenceClassification`, `ErnieForTokenClassification`, `FuyuForCausalLM`, `MiniMaxForCausalLM`, `MusicFlamingoForConditionalGeneration`, `PersimmonForCausalLM`.
- **Removed in `0.10.0` (15)** — vLLM dropped native support and the Transformers backend cannot serve them: no HF class (`ArcticForCausalLM`, `Cheers`, `CheersForConditionalGeneration`, `Fairseq2LlamaForCausalLM`, `FireRedLIDForConditionalGeneration`, `GritLM`, `HCXVisionForCausalLM`, `MPTForCausalLM`, `OuroForCausalLM`, `Plamo2ForCausalLM`, `RWForCausalLM`, `StableLMEpochForCausalLM`), backend-incompatible (`MptForCausalLM`), superseded by the generic `Terratorch` arch (`PrithviGeoSpatialMAE`), or renamed (`ExaoneMoEForCausalLM` → `ExaoneMoeForCausalLM`; `v0.31.0` registers only the new casing).

`supports_lora` / `supports_pipeline_parallelism` in `model_architectures.json` come from vLLM's own `supports_lora()` / `supports_pp()` on the class the CUDA image loads (for the per-device `vllm.models.*` packages, the `nvidia/` implementation); the Transformers-backend survivors take the flags of the backend classes (`Transformers*`), which support both. These flags are global, not per device: on the CPU build `DeepseekV4ForCausalLM` has no LoRA, although the shared flag says it does.

Each version block in `engines.json` lists the tool and reasoning parsers its build registers. Parser rules are shared by every version of the engine, so `get-compatible-engines` skips a rule's (or architecture default's) parser on a version whose list does not include it.

Note: `scripts/arch_support_to_seeder.py` mirrors only vLLM's **native** registry (387); the 10 Transformers-backend entries are maintained on top of that in `engines.json` + `model_architectures.json`, so those files are intentionally a superset of the mirror.

### Upstream vLLM base and KV-cache features

Each engine version carries two more fields, returned by `/engine/get-compatible-engines` (bud-runtime FRD-023):

- **`upstream_vllm`**: the upstream vLLM release a vLLM build is based on, such as `0.31.0`, or a dev build with its
  commit such as `0.26.0.dev+481e481be`. budsim picks the planner's engine record by version and, for a build it has no
  record for, by this upstream minor.
- **`kv_features`**: the KV-cache features verified on this build. budsim and budcluster render a KV setting only for a
  feature the build lists, so a feature is listed only after it was verified on that build. The API refuses any name
  outside this set, which matches the simulator's `KV_FEATURES`:

  | feature | renders | list it once |
  |---|---|---|
  | `kv_events` | `--kv-events-config` (ZMQ on 5557/5558) and the `kv-events-enabled` label, for prefix-aware routing and KV metrics | the engine publishes `BlockStored` events with the request's salt |
  | `cache_salt` | the per-tenant cache salt | the engine honours `cache_salt` |
  | `cpu_offload_shm` | the CPU tier in register mode (vLLM's offloading connector on a `/dev/shm` region) | the tier stores and reloads on bare metal; a vGPU without host-pointer access to registered memory gets alloc mode instead |
  | `cpu_offload_host_alloc` | the CPU tier in alloc mode (driver-allocated pinned memory), for vGPUs | the build carries the alloc host-memory patch |
  | `cpu_offload_shm_per_copy` | register mode with one transfer per copy | the build carries the per-copy patch |
  | `kv_fp8` | FP8 KV cache | a 128K needle-in-a-haystack recall above 90% on each GPU generation the build serves |
  | `tiering_fs` | the node-local disk tier | the tier no longer stalls the engine (vLLM #49829) |

For the versions it lists, `budconnect/seeders/data/engines.json` is the source of truth for both fields, as it is for
their compatibilities: the seeder writes them for a new version and brings an existing one back in line at every start.
For any other version, set them through `PUT /engine/version/{id}` or the admin UI's version Edit. An empty list
withdraws every feature.

| build | `upstream_vllm` | `kv_features` |
|---|---|---|
| CUDA `0.10.0` | `0.31.0` | `cache_salt`, `cpu_offload_shm`, `kv_events` |
| CPU `0.10.0` | `0.31.0` | none yet |

CUDA `0.10.0` lists neither the alloc-mode tier nor per-copy transfers: both need a fork patch that the build does
not carry. It lists no FP8 KV until the needle-in-a-haystack run passes, and no disk tier. CPU `0.10.0` lists nothing
until it is verified; KV events and the cache salt were verified on CPU `0.6.0`.
