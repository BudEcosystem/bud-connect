import json
import sys


# yapf: disable
# Mirrored from /datadisk/ditto/vllm/vllm/model_executor/models/registry.py
_TEXT_GENERATION_MODELS = {
    # [Decoder-only]
    "AfmoeForCausalLM": ("afmoe", "AfmoeForCausalLM"),
    "ApertusForCausalLM": ("apertus", "ApertusForCausalLM"),
    "AquilaModel": ("llama", "LlamaForCausalLM"),
    "AquilaForCausalLM": ("llama", "LlamaForCausalLM"),  # AquilaChat2
    "ArceeForCausalLM": ("arcee", "ArceeForCausalLM"),
    "ArcticForCausalLM": ("arctic", "ArcticForCausalLM"),
    "AXK1ForCausalLM": ("AXK1", "AXK1ForCausalLM"),
    # baichuan-7b, upper case 'C' in the class name
    "BaiChuanForCausalLM": ("baichuan", "BaiChuanForCausalLM"),
    # baichuan-13b, lower case 'c' in the class name
    "BaichuanForCausalLM": ("baichuan", "BaichuanForCausalLM"),
    "BailingMoeForCausalLM": ("bailing_moe", "BailingMoeForCausalLM"),
    "BailingMoeV2ForCausalLM": ("bailing_moe", "BailingMoeV2ForCausalLM"),
    "BailingMoeV2_5ForCausalLM": ("bailing_moe_linear", "BailingMoeV25ForCausalLM"),
    "BambaForCausalLM": ("bamba", "BambaForCausalLM"),
    "BloomForCausalLM": ("bloom", "BloomForCausalLM"),
    "ChatGLMModel": ("chatglm", "ChatGLMForCausalLM"),
    "ChatGLMForConditionalGeneration": ("chatglm", "ChatGLMForCausalLM"),
    "CohereForCausalLM": ("commandr", "CohereForCausalLM"),
    "Cohere2ForCausalLM": ("commandr", "CohereForCausalLM"),
    "Cohere2MoeForCausalLM": ("cohere2_moe", "Cohere2MoeForCausalLM"),
    "CwmForCausalLM": ("llama", "LlamaForCausalLM"),
    "DbrxForCausalLM": ("dbrx", "DbrxForCausalLM"),
    "DeciLMForCausalLM": ("nemotron_nas", "DeciLMForCausalLM"),
    "DeepseekForCausalLM": ("deepseek_v2", "DeepseekForCausalLM"),
    "DeepseekV2ForCausalLM": ("deepseek_v2", "DeepseekV2ForCausalLM"),
    "DeepseekV3ForCausalLM": ("deepseek_v2", "DeepseekV3ForCausalLM"),
    "DeepseekV32ForCausalLM": ("deepseek_v2", "DeepseekV3ForCausalLM"),
    "DeepseekV4ForCausalLM": ("vllm.models.deepseek_v4", "DeepseekV4ForCausalLM"),
    "Dots1ForCausalLM": ("dots1", "Dots1ForCausalLM"),
    "Ernie4_5ForCausalLM": ("ernie45", "Ernie4_5ForCausalLM"),
    "Ernie4_5_MoeForCausalLM": ("ernie45_moe", "Ernie4_5_MoeForCausalLM"),
    "ExaoneForCausalLM": ("exaone", "ExaoneForCausalLM"),
    "Exaone4ForCausalLM": ("exaone4", "Exaone4ForCausalLM"),
    "ExaoneMoEForCausalLM": ("exaone_moe", "ExaoneMoeForCausalLM"),
    "Fairseq2LlamaForCausalLM": ("fairseq2_llama", "Fairseq2LlamaForCausalLM"),
    "FalconForCausalLM": ("falcon", "FalconForCausalLM"),
    "FalconMambaForCausalLM": ("mamba", "MambaForCausalLM"),
    "FalconH1ForCausalLM": ("falcon_h1", "FalconH1ForCausalLM"),
    "FlexOlmoForCausalLM": ("flex_olmo", "FlexOlmoForCausalLM"),
    "GemmaForCausalLM": ("gemma", "GemmaForCausalLM"),
    "Gemma2ForCausalLM": ("gemma2", "Gemma2ForCausalLM"),
    "Gemma3ForCausalLM": ("gemma3", "Gemma3ForCausalLM"),
    "Rnj1ForCausalLM": ("rnj1", "Rnj1ForCausalLM"),
    "Gemma3nForCausalLM": ("gemma3n", "Gemma3nForCausalLM"),
    "Gemma4ForCausalLM": ("gemma4", "Gemma4ForCausalLM"),
    "Qwen3NextForCausalLM": ("qwen3_next", "Qwen3NextForCausalLM"),
    "GlmForCausalLM": ("glm", "GlmForCausalLM"),
    "Glm4ForCausalLM": ("glm4", "Glm4ForCausalLM"),
    "Glm4MoeForCausalLM": ("glm4_moe", "Glm4MoeForCausalLM"),
    "Glm4MoeLiteForCausalLM": ("glm4_moe_lite", "Glm4MoeLiteForCausalLM"),
    "GlmMoeDsaForCausalLM": ("deepseek_v2", "GlmMoeDsaForCausalLM"),
    "GptOssForCausalLM": ("gpt_oss", "GptOssForCausalLM"),
    "GPT2LMHeadModel": ("gpt2", "GPT2LMHeadModel"),
    "GPTBigCodeForCausalLM": ("gpt_bigcode", "GPTBigCodeForCausalLM"),
    "GPTJForCausalLM": ("gpt_j", "GPTJForCausalLM"),
    "GPTNeoXForCausalLM": ("gpt_neox", "GPTNeoXForCausalLM"),
    "GraniteForCausalLM": ("granite", "GraniteForCausalLM"),
    "GraniteMoeForCausalLM": ("granitemoe", "GraniteMoeForCausalLM"),
    "GraniteMoeHybridForCausalLM": ("granitemoehybrid", "GraniteMoeHybridForCausalLM"),
    "GraniteMoeSharedForCausalLM": ("granitemoeshared", "GraniteMoeSharedForCausalLM"),
    "GritLM": ("gritlm", "GritLM"),
    "Grok1ModelForCausalLM": ("grok1", "GrokForCausalLM"),
    "Grok1ForCausalLM": ("grok1", "GrokForCausalLM"),
    "HunYuanMoEV1ForCausalLM": ("hunyuan_v1", "HunYuanMoEV1ForCausalLM"),
    "HunYuanDenseV1ForCausalLM": ("hunyuan_v1", "HunYuanDenseV1ForCausalLM"),
    "HYV3ForCausalLM": ("hy_v3", "HYV3ForCausalLM"),
    "HCXVisionForCausalLM": ("hyperclovax_vision", "HCXVisionForCausalLM"),
    "HCXVisionV2ForCausalLM": ("hyperclovax_vision_v2", "HCXVisionV2ForCausalLM"),
    "HyperCLOVAXForCausalLM": ("hyperclovax", "HyperCLOVAXForCausalLM"),
    "InternLMForCausalLM": ("llama", "LlamaForCausalLM"),
    "InternLM2ForCausalLM": ("internlm2", "InternLM2ForCausalLM"),
    "InternLM2VEForCausalLM": ("internlm2_ve", "InternLM2VEForCausalLM"),
    "InternLM3ForCausalLM": ("llama", "LlamaForCausalLM"),
    "IQuestCoderForCausalLM": ("llama", "LlamaForCausalLM"),
    "IQuestLoopCoderForCausalLM": ("iquest_loopcoder", "IQuestLoopCoderForCausalLM"),
    "JAISLMHeadModel": ("jais", "JAISLMHeadModel"),
    "Jais2ForCausalLM": ("jais2", "Jais2ForCausalLM"),
    "JambaForCausalLM": ("jamba", "JambaForCausalLM"),
    "KimiLinearForCausalLM": ("kimi_linear", "KimiLinearForCausalLM"),
    "Lfm2ForCausalLM": ("lfm2", "Lfm2ForCausalLM"),
    "Lfm2MoeForCausalLM": ("lfm2_moe", "Lfm2MoeForCausalLM"),
    "LagunaForCausalLM": ("laguna", "LagunaForCausalLM"),
    "LlamaForCausalLM": ("llama", "LlamaForCausalLM"),
    "Llama4ForCausalLM": ("llama4", "Llama4ForCausalLM"),
    # For decapoda-research/llama-*
    "LLaMAForCausalLM": ("llama", "LlamaForCausalLM"),
    "LongcatFlashForCausalLM": ("longcat_flash", "LongcatFlashForCausalLM"),
    "MambaForCausalLM": ("mamba", "MambaForCausalLM"),
    "Mamba2ForCausalLM": ("mamba2", "Mamba2ForCausalLM"),
    "MiniCPMForCausalLM": ("minicpm", "MiniCPMForCausalLM"),
    "MiniCPM3ForCausalLM": ("minicpm3", "MiniCPM3ForCausalLM"),
    "MiniMaxForCausalLM": ("minimax_text_01", "MiniMaxText01ForCausalLM"),
    "MiniMaxText01ForCausalLM": ("minimax_text_01", "MiniMaxText01ForCausalLM"),
    "MiniMaxM1ForCausalLM": ("minimax_text_01", "MiniMaxText01ForCausalLM"),
    "MiniMaxM2ForCausalLM": ("minimax_m2", "MiniMaxM2ForCausalLM"),
    "Ministral3ForCausalLM": ("mistral", "MistralForCausalLM"),
    "MistralForCausalLM": ("mistral", "MistralForCausalLM"),
    "MistralLarge3ForCausalLM": ("mistral_large_3", "MistralLarge3ForCausalLM"),
    "MixtralForCausalLM": ("mixtral", "MixtralForCausalLM"),
    # transformers's mpt class has lower case
    "MptForCausalLM": ("mpt", "MPTForCausalLM"),
    "MPTForCausalLM": ("mpt", "MPTForCausalLM"),
    "MiMoForCausalLM": ("mimo", "MiMoForCausalLM"),
    "MiMoV2FlashForCausalLM": ("mimo_v2", "MiMoV2FlashForCausalLM"),
    "MiMoV2ForCausalLM": ("mimo_v2", "MiMoV2ForCausalLM"),
    "NemotronForCausalLM": ("nemotron", "NemotronForCausalLM"),
    "NemotronHForCausalLM": ("nemotron_h", "NemotronHForCausalLM"),
    "NemotronHPuzzleForCausalLM": ("nemotron_h", "NemotronHForCausalLM"),
    "OlmoForCausalLM": ("olmo", "OlmoForCausalLM"),
    "Olmo2ForCausalLM": ("olmo2", "Olmo2ForCausalLM"),
    "Olmo3ForCausalLM": ("olmo2", "Olmo2ForCausalLM"),
    "OlmoHybridForCausalLM": ("olmo_hybrid", "OlmoHybridForCausalLM"),
    "OlmoeForCausalLM": ("olmoe", "OlmoeForCausalLM"),
    "OPTForCausalLM": ("opt", "OPTForCausalLM"),
    "OrionForCausalLM": ("orion", "OrionForCausalLM"),
    "OuroForCausalLM": ("ouro", "OuroForCausalLM"),
    "PanguEmbeddedForCausalLM": ("openpangu", "PanguEmbeddedForCausalLM"),
    "PanguProMoEV2ForCausalLM": ("openpangu", "PanguProMoEV2ForCausalLM"),
    "PanguUltraMoEForCausalLM": ("openpangu", "PanguUltraMoEForCausalLM"),
    "Param2MoEForCausalLM": ("param2moe", "Param2MoEForCausalLM"),
    "PersimmonForCausalLM": ("persimmon", "PersimmonForCausalLM"),
    "PhiForCausalLM": ("phi", "PhiForCausalLM"),
    "Phi3ForCausalLM": ("phi3", "Phi3ForCausalLM"),
    "PhiMoEForCausalLM": ("phimoe", "PhiMoEForCausalLM"),
    "Plamo2ForCausalLM": ("plamo2", "Plamo2ForCausalLM"),
    "Plamo3ForCausalLM": ("plamo3", "Plamo3ForCausalLM"),
    "QWenLMHeadModel": ("qwen", "QWenLMHeadModel"),
    "Qwen2ForCausalLM": ("qwen2", "Qwen2ForCausalLM"),
    "Qwen2MoeForCausalLM": ("qwen2_moe", "Qwen2MoeForCausalLM"),
    "Qwen3ForCausalLM": ("qwen3", "Qwen3ForCausalLM"),
    "Qwen3MoeForCausalLM": ("qwen3_moe", "Qwen3MoeForCausalLM"),
    "RWForCausalLM": ("falcon", "FalconForCausalLM"),
    "SarvamMoEForCausalLM": ("sarvam", "SarvamMoEForCausalLM"),
    "SarvamMLAForCausalLM": ("sarvam", "SarvamMLAForCausalLM"),
    "SeedOssForCausalLM": ("seed_oss", "SeedOssForCausalLM"),
    "Step1ForCausalLM": ("step1", "Step1ForCausalLM"),
    "Step3TextForCausalLM": ("step3_text", "Step3TextForCausalLM"),
    "Step3p5ForCausalLM": ("step3p5", "Step3p5ForCausalLM"),
    "StableLMEpochForCausalLM": ("stablelm", "StablelmForCausalLM"),
    "StableLmForCausalLM": ("stablelm", "StablelmForCausalLM"),
    "Starcoder2ForCausalLM": ("starcoder2", "Starcoder2ForCausalLM"),
    "SolarForCausalLM": ("solar", "SolarForCausalLM"),
    "TeleChatForCausalLM": ("telechat2", "TeleChat2ForCausalLM"),
    "TeleChat2ForCausalLM": ("telechat2", "TeleChat2ForCausalLM"),
    "TeleChat3ForCausalLM": ("llama", "LlamaForCausalLM"),
    "TeleFLMForCausalLM": ("teleflm", "TeleFLMForCausalLM"),
    "XverseForCausalLM": ("llama", "LlamaForCausalLM"),
    "Zamba2ForCausalLM": ("zamba2", "Zamba2ForCausalLM"),
}

_EMBEDDING_MODELS = {
    # [Text-only]
    "BertModel": ("bert", "BertEmbeddingModel"),
    "BertSpladeSparseEmbeddingModel": ("bert", "BertSpladeSparseEmbeddingModel"),
    "ErnieModel": ("ernie", "ErnieEmbeddingModel"),
    "BgeM3EmbeddingModel": ("roberta", "BgeM3EmbeddingModel"),
    "DeciLMForCausalLM": ("nemotron_nas", "DeciLMForCausalLM"),
    "Gemma2Model": ("gemma2", "Gemma2ForCausalLM"),
    "Gemma3TextModel": ("gemma3", "Gemma3Model"),
    "GlmForCausalLM": ("glm", "GlmForCausalLM"),
    "GritLM": ("gritlm", "GritLM"),
    "GteModel": ("bert_with_rope", "SnowflakeGteNewModel"),
    "GteNewModel": ("bert_with_rope", "GteNewModel"),
    "JinaEmbeddingsV5Model": ("jina", "JinaEmbeddingsV5Model"),
    "LlamaBidirectionalModel": ("llama", "LlamaBidirectionalModel"),
    "LlamaModel": ("llama", "LlamaForCausalLM"),
    **{
        # Multiple models share the same architecture, so we include them all
        k: (mod, arch)
        for k, (mod, arch) in _TEXT_GENERATION_MODELS.items()
        if arch == "LlamaForCausalLM"
    },
    "MistralModel": ("llama", "LlamaForCausalLM"),
    "ModernBertModel": ("modernbert", "ModernBertModel"),
    "NomicBertModel": ("bert_with_rope", "NomicBertModel"),
    "Phi3ForCausalLM": ("phi3", "Phi3ForCausalLM"),
    "Qwen2Model": ("qwen2", "Qwen2ForCausalLM"),
    "Qwen2ForCausalLM": ("qwen2", "Qwen2ForCausalLM"),
    "RobertaForMaskedLM": ("roberta", "RobertaEmbeddingModel"),
    "RobertaModel": ("roberta", "RobertaEmbeddingModel"),
    "TeleChatForCausalLM": ("telechat2", "TeleChat2ForCausalLM"),
    "TeleChat2ForCausalLM": ("telechat2", "TeleChat2ForCausalLM"),
    "VoyageQwen3BidirectionalEmbedModel": (
        "voyage",
        "VoyageQwen3BidirectionalEmbedModel",
    ),
    "XLMRobertaModel": ("roberta", "RobertaEmbeddingModel"),
    # [Multimodal]
    "CLIPModel": ("clip", "CLIPEmbeddingModel"),
    "ColPaliForRetrieval": ("colpali", "ColPaliModel"),
    "LlamaNemotronVLModel": ("nemotron_vl", "LlamaNemotronVLForEmbedding"),
    "LlavaNextForConditionalGeneration": (
        "llava_next",
        "LlavaNextForConditionalGeneration",
    ),
    "Phi3VForCausalLM": ("phi3v", "Phi3VForCausalLM"),
    "Qwen2VLForConditionalGeneration": ("qwen2_vl", "Qwen2VLForConditionalGeneration"),
    "SiglipModel": ("siglip", "SiglipEmbeddingModel"),
    # Technically Terratorch models work on images, both in
    # input and output. I am adding it here because it piggy-backs on embedding
    # models for the time being.
    "PrithviGeoSpatialMAE": ("terratorch", "Terratorch"),
    "Terratorch": ("terratorch", "Terratorch"),
}

_LATE_INTERACTION_MODELS = {
    # [Text-only]
    "HF_ColBERT": ("colbert", "ColBERTModel"),
    "ColBERTModernBertModel": ("colbert", "ColBERTModernBertModel"),
    "ColBERTJinaRobertaModel": ("colbert", "ColBERTJinaRobertaModel"),
    "ColBERTLfm2Model": ("colbert", "ColBERTLfm2Model"),
    "JinaForRanking": ("jina", "JinaForRanking"),
    # [Multimodal]
    "ColModernVBertForRetrieval": ("colmodernvbert", "ColModernVBertForRetrieval"),
    "ColPaliForRetrieval": ("colpali", "ColPaliModel"),
    "ColQwen3": ("colqwen3", "ColQwen3Model"),
    "OpsColQwen3Model": ("colqwen3", "ColQwen3Model"),
    "ColQwen3_5": ("colqwen3_5", "ColQwen3_5Model"),
    "Qwen3VLNemotronEmbedModel": ("colqwen3", "ColQwen3Model"),
}

_REWARD_MODELS = {
    "InternLM2ForRewardModel": ("internlm2", "InternLM2ForRewardModel"),
    "Qwen2ForRewardModel": ("qwen2_rm", "Qwen2ForRewardModel"),
    "Qwen2ForProcessRewardModel": ("qwen2_rm", "Qwen2ForProcessRewardModel"),
}

_TOKEN_CLASSIFICATION_MODELS = {
    "BertForTokenClassification": ("bert", "BertForTokenClassification"),
    "ErnieForTokenClassification": ("ernie", "ErnieForTokenClassification"),
    "ModernBertForTokenClassification": (
        "modernbert",
        "ModernBertForTokenClassification",
    ),
    "Qwen3ASRForcedAlignerForTokenClassification": (
        "qwen3_asr_forced_aligner",
        "Qwen3ASRForcedAlignerForTokenClassification",
    ),
}

_SEQUENCE_CLASSIFICATION_MODELS = {
    "BertForSequenceClassification": ("bert", "BertForSequenceClassification"),
    "GPT2ForSequenceClassification": ("gpt2", "GPT2ForSequenceClassification"),
    "ErnieForSequenceClassification": ("ernie", "ErnieForSequenceClassification"),
    "GteNewForSequenceClassification": (
        "bert_with_rope",
        "GteNewForSequenceClassification",
    ),
    "JambaForSequenceClassification": ("jamba", "JambaForSequenceClassification"),
    "LlamaBidirectionalForSequenceClassification": (
        "llama",
        "LlamaBidirectionalForSequenceClassification",
    ),
    "ModernBertForSequenceClassification": (
        "modernbert",
        "ModernBertForSequenceClassification",
    ),
    "RobertaForSequenceClassification": ("roberta", "RobertaForSequenceClassification"),
    "XLMRobertaForSequenceClassification": (
        "roberta",
        "RobertaForSequenceClassification",
    ),
    # [Multimodal]
    "JinaVLForRanking": ("jina_vl", "JinaVLForSequenceClassification"),
    "LlamaNemotronVLForSequenceClassification": (
        "nemotron_vl",
        "LlamaNemotronVLForSequenceClassification",
    ),
}

# Retained as alias for backwards compat with arch_support_to_model_architectures.py
_CROSS_ENCODER_MODELS = _SEQUENCE_CLASSIFICATION_MODELS

_MULTIMODAL_MODELS = {
    # [Decoder-only]
    "AriaForConditionalGeneration": ("aria", "AriaForConditionalGeneration"),
    "AudioFlamingo3ForConditionalGeneration": (
        "audioflamingo3",
        "AudioFlamingo3ForConditionalGeneration",
    ),
    "MusicFlamingoForConditionalGeneration": (
        "musicflamingo",
        "MusicFlamingoForConditionalGeneration",
    ),
    "AyaVisionForConditionalGeneration": (
        "aya_vision",
        "AyaVisionForConditionalGeneration",
    ),
    "BagelForConditionalGeneration": ("bagel", "BagelForConditionalGeneration"),
    "BeeForConditionalGeneration": ("bee", "BeeForConditionalGeneration"),
    "Blip2ForConditionalGeneration": ("blip2", "Blip2ForConditionalGeneration"),
    "ChameleonForConditionalGeneration": (
        "chameleon",
        "ChameleonForConditionalGeneration",
    ),
    "Cheers": ("cheers", "CheersForConditionalGeneration"),
    "CheersForConditionalGeneration": ("cheers", "CheersForConditionalGeneration"),
    "Cohere2VisionForConditionalGeneration": (
        "cohere2_vision",
        "Cohere2VisionForConditionalGeneration",
    ),
    "DeepseekVLV2ForCausalLM": ("deepseek_vl2", "DeepseekVLV2ForCausalLM"),
    "DeepseekOCRForCausalLM": ("deepseek_ocr", "DeepseekOCRForCausalLM"),
    "DeepseekOCR2ForCausalLM": ("deepseek_ocr2", "DeepseekOCR2ForCausalLM"),
    "DotsOCRForCausalLM": ("dots_ocr", "DotsOCRForCausalLM"),
    "Eagle2_5_VLForConditionalGeneration": (
        "eagle2_5_vl",
        "Eagle2_5_VLForConditionalGeneration",
    ),
    "Ernie4_5_VLMoeForConditionalGeneration": (
        "ernie45_vl",
        "Ernie4_5_VLMoeForConditionalGeneration",
    ),
    "Exaone4_5_ForConditionalGeneration": (
        "exaone4_5",
        "Exaone4_5_ForConditionalGeneration",
    ),
    "FireRedASR2ForConditionalGeneration": (
        "fireredasr2",
        "FireRedASR2ForConditionalGeneration",
    ),
    "FunASRForConditionalGeneration": ("funasr", "FunASRForConditionalGeneration"),
    "FireRedLIDForConditionalGeneration": (
        "fireredlid",
        "FireRedLIDForConditionalGeneration",
    ),
    "FunAudioChatForConditionalGeneration": (
        "funaudiochat",
        "FunAudioChatForConditionalGeneration",
    ),
    "FuyuForCausalLM": ("fuyu", "FuyuForCausalLM"),
    "Gemma3ForConditionalGeneration": ("gemma3_mm", "Gemma3ForConditionalGeneration"),
    "Gemma3nForConditionalGeneration": (
        "gemma3n_mm",
        "Gemma3nForConditionalGeneration",
    ),
    "Gemma4ForConditionalGeneration": ("gemma4_mm", "Gemma4ForConditionalGeneration"),
    "GlmAsrForConditionalGeneration": ("glmasr", "GlmAsrForConditionalGeneration"),
    "GLM4VForCausalLM": ("glm4v", "GLM4VForCausalLM"),
    "Glm4vForConditionalGeneration": ("glm4_1v", "Glm4vForConditionalGeneration"),
    "Glm4vMoeForConditionalGeneration": ("glm4_1v", "Glm4vMoeForConditionalGeneration"),
    "GlmOcrForConditionalGeneration": ("glm_ocr", "GlmOcrForConditionalGeneration"),
    "GraniteSpeechForConditionalGeneration": (
        "granite_speech",
        "GraniteSpeechForConditionalGeneration",
    ),
    "Granite4VisionForConditionalGeneration": (
        "granite4_vision",
        "Granite4VisionForConditionalGeneration",
    ),
    "H2OVLChatModel": ("h2ovl", "H2OVLChatModel"),
    "HunYuanVLForConditionalGeneration": (
        "hunyuan_vision",
        "HunYuanVLForConditionalGeneration",
    ),
    "InternVLChatModel": ("internvl", "InternVLChatModel"),
    "InternS1ForConditionalGeneration": (
        "interns1",
        "InternS1ForConditionalGeneration",
    ),
    "InternVLForConditionalGeneration": (
        "interns1",
        "InternS1ForConditionalGeneration",
    ),
    "InternS1ProForConditionalGeneration": (
        "interns1_pro",
        "InternS1ProForConditionalGeneration",
    ),
    "InternS2PreviewForConditionalGeneration": (
        "interns2_preview",
        "InternS2PreviewForConditionalGeneration",
    ),
    "Idefics3ForConditionalGeneration": (
        "idefics3",
        "Idefics3ForConditionalGeneration",
    ),
    "IsaacForConditionalGeneration": ("isaac", "IsaacForConditionalGeneration"),
    "KananaVForConditionalGeneration": ("kanana_v", "KananaVForConditionalGeneration"),
    "KeyeForConditionalGeneration": ("keye", "KeyeForConditionalGeneration"),
    "KeyeVL1_5ForConditionalGeneration": (
        "keye_vl1_5",
        "KeyeVL1_5ForConditionalGeneration",
    ),
    "KimiVLForConditionalGeneration": ("kimi_vl", "KimiVLForConditionalGeneration"),
    "KimiK25ForConditionalGeneration": ("kimi_k25", "KimiK25ForConditionalGeneration"),
    "MoonshotKimiaForCausalLM": ("kimi_audio", "KimiAudioForConditionalGeneration"),
    "LightOnOCRForConditionalGeneration": (
        "lightonocr",
        "LightOnOCRForConditionalGeneration",
    ),
    "Lfm2VlForConditionalGeneration": ("lfm2_vl", "Lfm2VLForConditionalGeneration"),
    "Llama4ForConditionalGeneration": ("mllama4", "Llama4ForConditionalGeneration"),
    "Llama_Nemotron_Nano_VL": ("nemotron_vl", "LlamaNemotronVLChatModel"),
    "LlavaForConditionalGeneration": ("llava", "LlavaForConditionalGeneration"),
    "LlavaNextForConditionalGeneration": (
        "llava_next",
        "LlavaNextForConditionalGeneration",
    ),
    "LlavaNextVideoForConditionalGeneration": (
        "llava_next_video",
        "LlavaNextVideoForConditionalGeneration",
    ),
    "LlavaOnevisionForConditionalGeneration": (
        "llava_onevision",
        "LlavaOnevisionForConditionalGeneration",
    ),
    "MantisForConditionalGeneration": ("llava", "MantisForConditionalGeneration"),
    "MiDashengLMModel": ("midashenglm", "MiDashengLMModel"),
    "MiMoV2OmniForCausalLM": ("mimo_v2_omni", "MiMoV2OmniForCausalLM"),
    "MiniMaxVL01ForConditionalGeneration": (
        "minimax_vl_01",
        "MiniMaxVL01ForConditionalGeneration",
    ),
    "MiniCPMO": ("minicpmo", "MiniCPMO"),
    "MiniCPMV": ("minicpmv", "MiniCPMV"),
    "MiniCPMV4_6ForConditionalGeneration": (
        "minicpmv4_6",
        "MiniCPMV4_6ForConditionalGeneration",
    ),
    "Mistral3ForConditionalGeneration": (
        "mistral3",
        "Mistral3ForConditionalGeneration",
    ),
    "MolmoForCausalLM": ("molmo", "MolmoForCausalLM"),
    "Molmo2ForConditionalGeneration": ("molmo2", "Molmo2ForConditionalGeneration"),
    "Moondream3ForCausalLM": ("moondream3", "Moondream3ForCausalLM"),
    "HfMoondream": ("moondream3", "Moondream3ForCausalLM"),
    "NemotronH_Nano_VL_V2": ("nano_nemotron_vl", "NemotronH_Nano_VL_V2"),
    "NemotronH_Nano_Omni_Reasoning_V3": ("nano_nemotron_vl", "NemotronH_Nano_VL_V2"),
    "NemotronH_Super_Omni_Reasoning_V3": ("nano_nemotron_vl", "NemotronH_Nano_VL_V2"),
    "NVLM_D": ("nvlm_d", "NVLM_D_Model"),
    "OpenCUAForConditionalGeneration": ("opencua", "OpenCUAForConditionalGeneration"),
    "OpenPanguVLForConditionalGeneration": (
        "openpangu_vl",
        "OpenPanguVLForConditionalGeneration",
    ),
    "OpenVLAForActionPrediction": ("openvla", "OpenVLAForActionPrediction"),
    "Ovis": ("ovis", "Ovis"),
    "Ovis2_5": ("ovis2_5", "Ovis2_5"),
    "Ovis2_6ForCausalLM": ("ovis2_5", "Ovis2_5"),
    "Ovis2_6_MoeForCausalLM": ("ovis2_5", "Ovis2_5"),
    "PaddleOCRVLForConditionalGeneration": (
        "paddleocr_vl",
        "PaddleOCRVLForConditionalGeneration",
    ),
    "PaliGemmaForConditionalGeneration": (
        "paligemma",
        "PaliGemmaForConditionalGeneration",
    ),
    "Phi3VForCausalLM": ("phi3v", "Phi3VForCausalLM"),
    "Phi4ForCausalLMV": ("phi4siglip", "Phi4ForCausalLMV"),
    "Phi4MMForCausalLM": ("phi4mm", "Phi4MMForCausalLM"),
    "PixtralForConditionalGeneration": ("pixtral", "PixtralForConditionalGeneration"),
    "QianfanOCRForConditionalGeneration": (
        "qianfan_ocr",
        "QianfanOCRForConditionalGeneration",
    ),
    "QwenVLForConditionalGeneration": ("qwen_vl", "QwenVLForConditionalGeneration"),
    "Qwen2VLForConditionalGeneration": ("qwen2_vl", "Qwen2VLForConditionalGeneration"),
    "Qwen2_5_VLForConditionalGeneration": (
        "qwen2_5_vl",
        "Qwen2_5_VLForConditionalGeneration",
    ),
    "Qwen2AudioForConditionalGeneration": (
        "qwen2_audio",
        "Qwen2AudioForConditionalGeneration",
    ),
    "Qwen2_5OmniModel": (
        "qwen2_5_omni_thinker",
        "Qwen2_5OmniThinkerForConditionalGeneration",
    ),
    "Qwen2_5OmniForConditionalGeneration": (
        "qwen2_5_omni_thinker",
        "Qwen2_5OmniThinkerForConditionalGeneration",
    ),
    "Qwen3OmniMoeForConditionalGeneration": (
        "qwen3_omni_moe_thinker",
        "Qwen3OmniMoeThinkerForConditionalGeneration",
    ),
    "Qwen3ASRForConditionalGeneration": (
        "qwen3_asr",
        "Qwen3ASRForConditionalGeneration",
    ),
    "Qwen3ASRRealtimeGeneration": ("qwen3_asr_realtime", "Qwen3ASRRealtimeGeneration"),
    "Qwen3VLForConditionalGeneration": ("qwen3_vl", "Qwen3VLForConditionalGeneration"),
    "Qwen3VLMoeForConditionalGeneration": (
        "qwen3_vl_moe",
        "Qwen3VLMoeForConditionalGeneration",
    ),
    "Qwen3_5ForConditionalGeneration": ("qwen3_5", "Qwen3_5ForConditionalGeneration"),
    "Qwen3_5MoeForConditionalGeneration": (
        "qwen3_5",
        "Qwen3_5MoeForConditionalGeneration",
    ),
    "RForConditionalGeneration": ("rvl", "RForConditionalGeneration"),
    "SkyworkR1VChatModel": ("skyworkr1v", "SkyworkR1VChatModel"),
    "SmolVLMForConditionalGeneration": ("smolvlm", "SmolVLMForConditionalGeneration"),
    "StepVLForConditionalGeneration": ("step_vl", "StepVLForConditionalGeneration"),
    "Step3VLForConditionalGeneration": ("step3_vl", "Step3VLForConditionalGeneration"),
    "TarsierForConditionalGeneration": ("tarsier", "TarsierForConditionalGeneration"),
    "Tarsier2ForConditionalGeneration": (
        "qwen2_vl",
        "Tarsier2ForConditionalGeneration",
    ),
    "UltravoxModel": ("ultravox", "UltravoxModel"),
    "VoxtralForConditionalGeneration": ("voxtral", "VoxtralForConditionalGeneration"),
    "VoxtralRealtimeGeneration": ("voxtral_realtime", "VoxtralRealtimeGeneration"),
    # [Encoder-decoder]
    "CohereAsrForConditionalGeneration": (
        "cohere_asr",
        "CohereAsrForConditionalGeneration",
    ),
    "NemotronParseForConditionalGeneration": (
        "nemotron_parse",
        "NemotronParseForConditionalGeneration",
    ),
    "WhisperForConditionalGeneration": ("whisper", "WhisperForConditionalGeneration"),
}

_SPECULATIVE_DECODING_MODELS = {
    "ExtractHiddenStatesModel": ("extract_hidden_states", "ExtractHiddenStatesModel"),
    "MiMoMTPModel": ("mimo_mtp", "MiMoMTP"),
    "MiMoV2MTPModel": ("mimo_v2_mtp", "MiMoV2MTP"),
    "MiMoV2OmniMTPModel": ("mimo_v2_mtp", "MiMoV2OmniMTP"),
    "EagleCohereForCausalLM": ("cohere_eagle", "EagleCohereForCausalLM"),
    "EagleLlamaForCausalLM": ("llama_eagle", "EagleLlamaForCausalLM"),
    "EagleLlama4ForCausalLM": ("llama4_eagle", "EagleLlama4ForCausalLM"),
    "EagleMiniCPMForCausalLM": ("minicpm_eagle", "EagleMiniCPMForCausalLM"),
    "DFlashDraftModel": ("qwen3_dflash", "DFlashQwen3ForCausalLM"),
    "PEagleDraftModel": ("llama_eagle3", "Eagle3LlamaForCausalLM"),
    "PeagleLlamaForCausalLM": ("llama_eagle3", "Eagle3LlamaForCausalLM"),
    "Eagle3LlamaForCausalLM": ("llama_eagle3", "Eagle3LlamaForCausalLM"),
    "Eagle3MiniMaxM2ForCausalLM": ("llama_eagle3", "Eagle3LlamaForCausalLM"),
    "LlamaForCausalLMEagle3": ("llama_eagle3", "Eagle3LlamaForCausalLM"),
    "Eagle3Qwen2_5vlForCausalLM": ("llama_eagle3", "Eagle3LlamaForCausalLM"),
    "Eagle3Qwen3vlForCausalLM": ("llama_eagle3", "Eagle3LlamaForCausalLM"),
    "EagleMistralForCausalLM": ("mistral_eagle", "EagleMistralForCausalLM"),
    "EagleMistralLarge3ForCausalLM": (
        "mistral_large_3_eagle",
        "EagleMistralLarge3ForCausalLM",
    ),
    "Eagle3DeepseekV2ForCausalLM": ("deepseek_eagle3", "Eagle3DeepseekV2ForCausalLM"),
    "Eagle3DeepseekV3ForCausalLM": ("deepseek_eagle3", "Eagle3DeepseekV2ForCausalLM"),
    "EagleDeepSeekMTPModel": ("deepseek_eagle", "EagleDeepseekV3ForCausalLM"),
    "DeepSeekMTPModel": ("deepseek_mtp", "DeepSeekMTP"),
    "DeepSeekV4MTPModel": ("vllm.models.deepseek_v4", "DeepSeekV4MTP"),
    "Gemma4MTPModel": ("gemma4_mtp", "Gemma4MTP"),
    "ErnieMTPModel": ("ernie_mtp", "ErnieMTP"),
    "ExaoneMoeMTP": ("exaone_moe_mtp", "ExaoneMoeMTP"),
    "Exaone4_5_MTP": ("exaone4_5_mtp", "Exaone4_5_MTP"),
    "NemotronHMTPModel": ("nemotron_h_mtp", "NemotronHMTP"),
    "LongCatFlashMTPModel": ("longcat_flash_mtp", "LongCatFlashMTP"),
    "Glm4MoeMTPModel": ("glm4_moe_mtp", "Glm4MoeMTP"),
    "Glm4MoeLiteMTPModel": ("glm4_moe_lite_mtp", "Glm4MoeLiteMTP"),
    "GlmOcrMTPModel": ("glm_ocr_mtp", "GlmOcrMTP"),
    "MedusaModel": ("medusa", "Medusa"),
    "OpenPanguMTPModel": ("openpangu_mtp", "OpenPanguMTP"),
    "Qwen3NextMTP": ("qwen3_next_mtp", "Qwen3NextMTP"),
    "Step3p5MTP": ("step3p5_mtp", "Step3p5MTP"),
    "Qwen3_5MTP": ("qwen3_5_mtp", "Qwen3_5MTP"),
    "Qwen3_5MoeMTP": ("qwen3_5_mtp", "Qwen3_5MoeMTP"),
    "HYV3MTPModel": ("hy_v3_mtp", "HYV3MTP"),
    # Temporarily disabled.
    # # TODO(woosuk): Re-enable this once the MLP Speculator is supported in V1.
    # "MLPSpeculatorPreTrainedModel": ("mlp_speculator", "MLPSpeculator"),
}

_TRANSFORMERS_SUPPORTED_MODELS = {
    # Text generation models
    "SmolLM3ForCausalLM": ("transformers", "TransformersForCausalLM"),
    # Multimodal models
    "Emu3ForConditionalGeneration": (
        "transformers",
        "TransformersMultiModalForCausalLM",
    ),
}

_TRANSFORMERS_BACKEND_MODELS = {
    # Text generation models
    "TransformersForCausalLM": ("transformers", "TransformersForCausalLM"),
    "TransformersMoEForCausalLM": ("transformers", "TransformersMoEForCausalLM"),
    # Multimodal models
    "TransformersMultiModalForCausalLM": (
        "transformers",
        "TransformersMultiModalForCausalLM",
    ),
    "TransformersMultiModalMoEForCausalLM": (
        "transformers",
        "TransformersMultiModalMoEForCausalLM",
    ),
    # Embedding models
    "TransformersEmbeddingModel": ("transformers", "TransformersEmbeddingModel"),
    "TransformersMoEEmbeddingModel": ("transformers", "TransformersMoEEmbeddingModel"),
    "TransformersMultiModalEmbeddingModel": (
        "transformers",
        "TransformersMultiModalEmbeddingModel",
    ),
    # Sequence classification models
    "TransformersForSequenceClassification": (
        "transformers",
        "TransformersForSequenceClassification",
    ),
    "TransformersMoEForSequenceClassification": (
        "transformers",
        "TransformersMoEForSequenceClassification",
    ),
    "TransformersMultiModalForSequenceClassification": (
        "transformers",
        "TransformersMultiModalForSequenceClassification",
    ),
}

_VLLM_MODELS = {
    **_TEXT_GENERATION_MODELS,
    **_EMBEDDING_MODELS,
    **_LATE_INTERACTION_MODELS,
    **_REWARD_MODELS,
    **_TOKEN_CLASSIFICATION_MODELS,
    **_SEQUENCE_CLASSIFICATION_MODELS,
    **_MULTIMODAL_MODELS,
    **_SPECULATIVE_DECODING_MODELS,
    **_TRANSFORMERS_SUPPORTED_MODELS,
    **_TRANSFORMERS_BACKEND_MODELS,
}


def build_arch_list() -> list:
    return list(_VLLM_MODELS.keys())


def write_arch_json(output_file: str) -> None:
    model_list = build_arch_list()
    print(model_list)
    output_data = {"architectures": model_list}
    output_json = json.dumps(output_data, indent=2, ensure_ascii=False)
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(output_json)
    print(f"Output written to: {output_file}", file=sys.stderr)


def main() -> None:
    write_arch_json("arch.json")


if __name__ == "__main__":
    main()
