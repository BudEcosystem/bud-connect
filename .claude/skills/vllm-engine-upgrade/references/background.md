# Background & rationale

Deeper context behind the SKILL.md steps. Read the section you need.

## Table of contents
1. vLLM's model-resolution order (why the Transformers-backend check is correct)
2. Why vLLM drops architectures (the four causes)
3. Worked example: the last upgrade (0.8.0 → 0.9.0)
4. Where the source-of-truth data lives inside vLLM

---

## 1. vLLM's model-resolution order

When vLLM loads a model it reads the HF config's `architectures` field and
resolves it in `vllm/model_executor/models/registry.py`
(`inspect_model_cls` / `resolve_model_cls`). With the default
`--model-impl auto`, the order is:

1. If the arch is in the native registry → use the native implementation.
2. If **no** arch is native → `_try_resolve_transformers(...)`: usable when HF
   Transformers has a class for that arch name (`getattr(transformers, arch)`)
   that passes `.is_backend_compatible()`, **or** the checkpoint's `auto_map`
   provides a backend-compatible custom class (trust_remote_code).
3. Only if that also fails → `_raise_for_unsupported(...)`, which is where the
   `_PREVIOUSLY_SUPPORTED_MODELS` message *"…was supported in vLLM until vX…"*
   comes from.

So `_PREVIOUSLY_SUPPORTED_MODELS` does **not** block the Transformers fallback —
it only produces a nicer error once everything else has failed. That is exactly
why a natively-dropped arch can still be deployable, and why
`check_transformers_backend.py` reproduces vLLM's precise gate
(`getattr(transformers, arch).is_backend_compatible()`).

Why exclude the `auto_map`/trust_remote_code path from the arch-level verdict:
it depends on the specific model repo, not the architecture name, so BudConnect
can't guarantee it for every checkpoint declaring that arch. For a pre-deploy
oracle a false "supported" (failed deployment) is worse than a false
"unsupported", so keep the verdict to the arch-level guarantee.

## 2. Why vLLM drops architectures

Weights on HuggingFace don't disappear; vLLM just deletes the in-tree modeling
code, tracked in `_PREVIOUSLY_SUPPORTED_MODELS` (arch → last-supported version).
Four recurring causes:

- **Redundant alias** of a supported arch — the entry was literally
  `("llama", "LlamaForCausalLM")` (e.g. `InternLMForCausalLM`, `Aquila*`,
  `XverseForCausalLM`) or aliased a newer sibling (`TeleChatForCausalLM` →
  TeleChat2). Real checkpoints declare the successor arch, which stays listed —
  so drop the alias name.
- **Superseded** by a newer generation — `QWen`/`QwenVL` → Qwen2/2.5/3,
  `MiniMax-M1/Text01/VL01` → M2/M3, BERT-era `Ernie*` → ERNIE 4.5, `JAIS` → JAIS2,
  `Tarsier` → Tarsier2.
- **Transformers major migration** (v4 → v5) — models tied to the old API were
  dropped rather than ported (marked `# last version with Transformers v4`).
- **Maintenance burden / low usage** — bespoke, rarely-served implementations
  deleted to shrink the code/test surface (Grok-1, Baichuan, Bamba, Dots1,
  Persimmon/Fuyu, Mantis, AyaVision, MusicFlamingo, Mono-InternVL).

A related but distinct cause, **V0→V1 engine deprecation**, removed some
encoder-decoder archs (Donut, Mllama) — worth checking on future upgrades.

## 3. Worked example — 0.8.0 → 0.9.0 (vLLM @ 481e481be, transformers 5.13.1)

- Native architectures: **361 → 354** (+22 new, −29 natively-dropped).
- Tool parsers: **25 → 43**; reasoning parsers: **13 → 27** (dropped the dead
  `minimax_m1`; `engines.json` had a stale `minimax` parser_rule → removed).
- Of the 29 natively-dropped, **9 stayed deployable via the Transformers backend**
  (`is_backend_compatible()==True`) and were kept:
  `AyaVisionForConditionalGeneration`, `Dots1ForCausalLM`, `ErnieModel`,
  `ErnieForSequenceClassification`, `ErnieForTokenClassification`,
  `FuyuForCausalLM`, `MiniMaxForCausalLM`,
  `MusicFlamingoForConditionalGeneration`, `PersimmonForCausalLM`.
- The other **20 were truly removed** — no HF class (`Grok1*`, `QWen`/`QwenVL`,
  `Baichuan*`, `JAIS`, `Mantis`, `MiniMaxM1/Text01/VL01`), backend-incompatible
  (`Bamba` — has a class but fails the gate), Transformers-v4-locked (`Tarsier*`),
  or Llama-family aliases (`InternLM*`, `Aquila*`, `Xverse`, `TeleChat`).
- Final compatibility set: **354 native + 9 survivors = 363** (CUDA == CPU ==
  model_architectures.json).
- Enrichment: 6 new chat archs got parsers (e.g. `MiniMaxM3Sparse*` → `minimax_m3`,
  `Gemma4Unified*` → `gemma4`, `Step3p7*` → `step3p5`, `Apertus*` → `apertus`,
  `GraniteMoeHybrid*` → `granite4`); most new archs (draft/MTP/audio/OCR/vision)
  stayed null; `MiniMaxM2ForCausalLM` reasoning moved `minimax_m2` →
  `minimax_m2_append_think` per `reasoning_outputs.md` (one behavioral overwrite).

## 4. Source-of-truth locations inside vLLM

Stable, but vLLM refactors — re-verify if the extractor errors.

- Architectures: `vllm/model_executor/models/registry.py` — the 10 dicts merged
  into `_VLLM_MODELS` (`_TEXT_GENERATION_MODELS`, `_EMBEDDING_MODELS`,
  `_LATE_INTERACTION_MODELS`, `_REWARD_MODELS`, `_TOKEN_CLASSIFICATION_MODELS`,
  `_SEQUENCE_CLASSIFICATION_MODELS`, `_MULTIMODAL_MODELS`,
  `_SPECULATIVE_DECODING_MODELS`, `_TRANSFORMERS_SUPPORTED_MODELS`,
  `_TRANSFORMERS_BACKEND_MODELS`). Excludes `_PREVIOUSLY_SUPPORTED_MODELS` and
  `_OOT_SUPPORTED_MODELS`.
- Tool parsers: `vllm/tool_parsers/__init__.py` → `_TOOL_PARSERS_TO_REGISTER` keys.
- Reasoning parsers: `vllm/reasoning/__init__.py` →
  `_REASONING_PARSERS_TO_REGISTER` keys.
- Recommended arch→parser mapping: `docs/features/tool_calling.md`,
  `docs/features/reasoning_outputs.md`.
- LoRA / PP flags: `docs/models/supported_models.md` (LoRA and PP columns), or the
  model class's `Supports*` interfaces.
- transformers pin (for the backend check): vLLM `requirements/*.txt`.
