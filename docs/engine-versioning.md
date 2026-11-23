# Engine Versioning


The engine versioning is a key component of the BudConnect service. It is responsible for storing the engine versions, model compatibilities, and other engine related resources.

For the vllm engine, the build will be done from the forked version of the vllm repo with required changes to support the bud stack. The versioning will not be same as the vllm repo. But the versoning will be done based on the releases of Bud. 

The engine images are published with version tags under `registry.bud.studio/runtime`; the image per device is listed below.

| Device Architecture | Image Name | Version |
| ------------------- | ---------- | ------- |
| cuda                | registry.bud.studio/runtime/vllm-cuda | 0.12.0  |
| cpu                 | registry.bud.studio/runtime/vllm-cpu | 0.12.0  |
| rocm                | registry.bud.studio/runtime/vllm-rocm | —       |
| hpu                 | registry.bud.studio/runtime/vllm-hpu | —       |

> Versions track Bud releases, not upstream vLLM, and each device build has its own version lineage. `0.12.0` (CUDA and CPU) is upstream vLLM `v0.34.0` (commit `62d4bc3c7`): the linux/amd64 images of `vllm/vllm-openai:v0.34.0` and `vllm/vllm-openai-cpu:v0.34.0`, copied unchanged, as `0.11.0` was for `v0.32.0`. Both ship `transformers 5.22.2`; the CPU image reports `vllm 0.34.0+cpu`, and its installed model code matches the tag. The previous builds were `0.11.0` (upstream `v0.32.0` @ `5df63a720`, `transformers 5.19.0`) and `0.10.0` (upstream `v0.31.0` @ `db9527a46`, `transformers 5.17.0`). ROCM/HPU images are not currently published. When bumping the version, refresh the vLLM-derived data in the same pass: `budconnect/seeders/data/engines.json` (architecture lists, per-version parser lists + `container_image`), `budconnect/seeders/data/model_architectures.json`, and the `_VLLM_MODELS` mirror in `scripts/arch_support_to_seeder.py`.

### Architecture support policy

The `0.12.0` CUDA compatibility list has **437** architectures = **426 natively supported** (vLLM's `_VLLM_MODELS` registry union) **+ 11 served via vLLM's Transformers backend**. The CPU list is the same minus 7 archs the CPU build cannot load (430):

- CPU stubs that raise `NotImplementedError`: `DeepseekV4ForConditionalGeneration`, `DeepSeekV4MTPModel` and `DSparkDraftModel` (DeepSeek-V4 MTP and DSpark speculative decoding are not implemented on CPU).
- Imports the CPU image cannot satisfy: `Dots3NoteForCausalLM` / `Dots3NoteMTPModel` (`vllm.third_party.deep_gemm`, a CUDA build), `KananaVForConditionalGeneration` (`timm`) and `Terratorch` (`terratorch`).

The last four came from a static walk of each arch's module-level imports over the CPU image's own `site-packages`. The two DeepSeek-V4 stubs and the two missing packages were already the same in `0.11.0`, whose CPU list still carried those archs. The CUDA image ships `timm` but not `terratorch`, so `Terratorch` needs `pip install terratorch` on top of the CUDA image as well; it stays on the CUDA list, which mirrors vLLM's registry.

BudConnect is a pre-deployment compatibility oracle, so an architecture stays listed as long as the engine can *deploy* it — natively **or** via the Transformers backend (which vLLM's default `--model-impl auto` uses automatically, per `_try_resolve_transformers` in `registry.py`). The per-arch test is HF Transformers' `getattr(transformers, ArchName).is_backend_compatible()`, run against the `transformers==5.22.2` that both `0.12.0` images ship. vLLM also accepts `_can_set_attn_implementation()`, but BudConnect keeps the stricter `is_backend_compatible()` test, and lists an arch only if the backend can serve its attention: the backend covers full/sliding attention in encoder-only, decoder-only and MoE models, and not encoder-decoder or cross-attention models. So `BambaForCausalLM` (hybrid Mamba) passes the looser gate but is not listed, and `MllamaForConditionalGeneration` (cross-attention to the vision encoder) passes `is_backend_compatible()` but is not listed either.

- **Kept via Transformers backend (11):** `AyaVisionForConditionalGeneration`, `ChameleonForConditionalGeneration`, `Dots1ForCausalLM`, `ErnieModel`, `ErnieForSequenceClassification`, `ErnieForTokenClassification`, `FuyuForCausalLM`, `MiniMaxForCausalLM`, `MusicFlamingoForConditionalGeneration`, `PersimmonForCausalLM` and `Phi4MultimodalForCausalLM`, the same 11 as `0.11.0`, all still passing under `transformers 5.22.2`.
- **Added in `0.12.0` (41):** `AliceAIForCausalLM`, `Alpamayo2Super`, `BeamForCausalLM`, `CanaryForConditionalGeneration`, `ClefFlashForJointSchema`, `ColUltraVBertForRetrieval`, `D3ForSequenceClassification`, `DFlash2BeamDraftModel`, `DFlash2RicursiveDraftModel`, `DFlashQwen3XPressModel`, `DSparkMiniMaxDraftModel`, `DomynEdgeForCausalLM`, `DoryForCausalLM`, `FlintForCausalLM`, `KimiK31ForConditionalGeneration`, `Kolibri1ForCausalLM`, `Lfm2BidirectionalModel`, `Lfm3AudioForConditionalGeneration`, `Lfm3ForCausalLM`, `Lfm3VlForConditionalGeneration`, `MingV3ASRForConditionalGeneration`, `MiniCPMOcrForConditionalGeneration`, `MistralLarge4DSparkModel`, `MistralLarge4ForCausalLM`, `ModernVBertModel`, `MuseSparkDSparkModel`, `MuseSparkForConditionalGeneration`, `Nemotron3_5TranscribeForConditionalGeneration`, `Nemotron3_5TranscribeMTPModel`, `ParseAuxMTPModel`, `Qwen3XPressModel`, `RadioMBartPrefixForCausalLM`, `RicursiveForCausalLM`, `Step5ForCausalLM`, `Step5ForConditionalGeneration`, `Step5MTP`, `TransformersForMTP`, `TransformersMoEForMTP`, `UltraVBertModel`, `UnlimitedOCR2TextForCausalLM`, `ZayaForCausalLM`.
- **Removed in `0.12.0` (6):** `KeyeForConditionalGeneration` and `KeyeVL1_5ForConditionalGeneration` (vLLM removed Keye-VL, #64287, and HF Transformers has no class for them), and the `MedusaModel`, `PEagleDraftModel`, `PeagleLlamaForCausalLM` and `PeagleQwen3ForCausalLM` draft heads, which `v0.34.0` no longer registers.
- **Moved to the Transformers backend:** `v0.32.0` moved `ArceeForCausalLM`, `CwmForCausalLM`, `GlmForCausalLM`, `GPTNeoXForCausalLM`, `Jais2ForCausalLM`, `MellumForCausalLM`, `PhiForCausalLM` and `SeedOssForCausalLM`; `v0.34.0` moves `AriaForConditionalGeneration`, `GemmaForCausalLM`, `OlmoeForCausalLM` and `StableLmForCausalLM`, and adds `Kolibri1ForCausalLM` there directly. vLLM registers them in `_TRANSFORMERS_SUPPORTED_MODELS`; they stay native (in `_VLLM_MODELS`) and listed, keep their HF `model_type` as family, and take the backend classes' flags.

`supports_lora` / `supports_pipeline_parallelism` in `model_architectures.json` come from vLLM's own `supports_lora()` / `supports_pp()` on the class the CUDA image loads (for the per-device `vllm.models.*` packages, the `nvidia/` implementation); the archs the Transformers backend serves take the flags of the backend classes (`Transformers*`), which support both. vLLM's docs table shows no LoRA for `GPTNeoXForCausalLM`, but the backend class it now loads accepts it. `v0.32.0` also adds LoRA to `BertEmbeddingModel`, so `BertModel`, `BertSpladeSparseEmbeddingModel`, `BgeM3EmbeddingModel`, `HF_ColBERT`, `RobertaModel`, `RobertaForMaskedLM` and `XLMRobertaModel` now list it. `v0.34.0` adds LoRA to `BertForSequenceClassification`, `BertForTokenClassification` and `DeepseekV41ForCausalLM`, and to `AriaForConditionalGeneration` and `StableLmForCausalLM` through the backend. These flags are global, not per device: on the CPU build `DeepseekV4ForCausalLM` has no LoRA, although the shared flag says it does.

Each version block in `engines.json` lists the tool and reasoning parsers its build registers. Parser rules are shared by every version of the engine, so `get-compatible-engines` skips a rule's (or architecture default's) parser on a version whose list does not include it. `0.12.0` has 62 tool and 44 reasoning parsers. It adds the `beam`, `granite_toolcall_parser`, `muse`, `musespark`, `ripple`, `step5`, `zaya` and `zaya_xml` tool parsers and the `beam`, `muse`, `musespark`, `ripple`, `step5` and `zaya` reasoning parsers. Following vLLM's docs, `BeamForCausalLM` defaults to `beam`, `MuseSparkForConditionalGeneration` to `muse`, `RicursiveForCausalLM` (Ripple) to `ripple`, `ZayaForCausalLM` to `zaya` and `Kolibri1ForCausalLM` to `hf`, for both tools and reasoning, and a prefix rule sends `ibm-granite/granite-4.2-` to `granite_toolcall_parser`. As in `0.10.0`, new models also take the parsers written for them or those of a sibling architecture: `Step5ForCausalLM` and `Step5ForConditionalGeneration` take `step5` for both (`Step5ToolParser` is written for Step-5's output; the `step5` reasoning parser is DeepSeek-R1's), `KimiK31ForConditionalGeneration` takes `kimi_k3` like `KimiK3ForConditionalGeneration`, whose class it shares, and `MistralLarge4ForCausalLM` takes the `mistral` tool parser like `MistralLarge3ForCausalLM`, with no reasoning parser. LFM3 keeps none, as LFM2 does, and draft, MTP, embedding, OCR and speech archs have none.

`v0.34.0` also changes runtime defaults that the deployment side may need to account for: `--block-size` defaults to 64 (was 16), the extensible KV cache is on and `gpu_memory_utilization` defaults to 1.0, Model Runner V1 is gone (`VLLM_USE_V2_MODEL_RUNNER=0` fails at startup), and `llama3_json` no longer streams tool arguments incrementally.

Note: `scripts/arch_support_to_seeder.py` mirrors only vLLM's **native** registry (426); the 11 Transformers-backend entries are maintained on top of that in `engines.json` + `model_architectures.json`, so those files are intentionally a superset of the mirror.

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
| CUDA `0.12.0` | `0.34.0` | `cache_salt`, `cpu_offload_shm`, `kv_events` |
| CPU `0.12.0` | `0.34.0` | `cache_salt`, `kv_events` |

Both `0.12.0` builds carry the `0.10.0` lists over, as `0.11.0` did, before the features have been re-run on them;
re-run each on the `0.12.0` build and withdraw any that fails. What `v0.34.0` changes for them:

- `kv_events`: `BlockStored` gains a trailing `lookahead_token_ids` field, omitted while lookahead hashing is off (the
  default), so the wire format is unchanged unless it is turned on. The default `--block-size` is now 64 (was 16), so
  each event covers 64 tokens; a consumer that assumes 16-token blocks must read `block_size` from the event, or the
  deployment must pass `--block-size 16`.
- `cache_salt`: unchanged; the salt still keys the first block's hash in `vllm/v1/core/kv_cache_utils.py`.
- `cpu_offload_shm`: `shared_offload_region.py`, `gpu_worker.py` and `manager.py` in `vllm/v1/kv_offload/cpu/` are
  reworked again, and the extensible KV cache (on by default) now sizes the GPU cache after warmup, so re-run
  store-and-reload and pinned bandwidth.

CUDA lists neither the alloc-mode tier nor per-copy transfers: both need a fork patch that the build does not carry. It
lists no FP8 KV until the needle-in-a-haystack run passes, and no disk tier. CPU lists the cache salt and KV events,
verified on `0.10.0` on PNAP (Xeon 6767P, 2026-11-06): a prompt sent with one salt hits its own blocks and misses under
another, and the engine publishes `BlockStored` events whose hashes differ by salt, which AIBrix v0.8.0's gateway
subscribes to. Its offloading tiers stay unlisted: vLLM's offloading connector refuses CPU engines.
