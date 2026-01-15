import json
import sys


# yapf: disable
_TEXT_GENERATION_MODELS = {
    # [Decoder-only]
    "ApertusForCausalLM": ("apertus", "ApertusForCausalLM"),
    "AquilaModel": ("llama", "LlamaForCausalLM"),
    "AquilaForCausalLM": ("llama", "LlamaForCausalLM"),  # AquilaChat2
    "ArceeForCausalLM": ("arcee", "ArceeForCausalLM"),
    "ArcticForCausalLM": ("arctic", "ArcticForCausalLM"),
    # baichuan-7b, upper case 'C' in the class name
    "BaiChuanForCausalLM": ("baichuan", "BaiChuanForCausalLM"),
    # baichuan-13b, lower case 'c' in the class name
    "BaichuanForCausalLM": ("baichuan", "BaichuanForCausalLM"),
    "BailingMoeForCausalLM": ("bailing_moe", "BailingMoeForCausalLM"),
    "BailingMoeV2ForCausalLM": ("bailing_moe", "BailingMoeV2ForCausalLM"),
    "BambaForCausalLM": ("bamba", "BambaForCausalLM"),
    "BloomForCausalLM": ("bloom", "BloomForCausalLM"),
    "ChatGLMModel": ("chatglm", "ChatGLMForCausalLM"),
    "ChatGLMForConditionalGeneration": ("chatglm", "ChatGLMForCausalLM"),
    "CohereForCausalLM": ("commandr", "CohereForCausalLM"),
    "Cohere2ForCausalLM": ("commandr", "CohereForCausalLM"),
    "CwmForCausalLM": ("llama", "LlamaForCausalLM"),
    "DbrxForCausalLM": ("dbrx", "DbrxForCausalLM"),
    "DeciLMForCausalLM": ("nemotron_nas", "DeciLMForCausalLM"),
    "DeepseekForCausalLM": ("deepseek_v2", "DeepseekForCausalLM"),
    "DeepseekV2ForCausalLM": ("deepseek_v2", "DeepseekV2ForCausalLM"),
    "DeepseekV3ForCausalLM": ("deepseek_v2", "DeepseekV3ForCausalLM"),
    "DeepseekV32ForCausalLM": ("deepseek_v2", "DeepseekV3ForCausalLM"),
    "Dots1ForCausalLM": ("dots1", "Dots1ForCausalLM"),
    "Ernie4_5ForCausalLM": ("ernie45", "Ernie4_5ForCausalLM"),
    "Ernie4_5_MoeForCausalLM": ("ernie45_moe", "Ernie4_5_MoeForCausalLM"),
    "ExaoneForCausalLM": ("exaone", "ExaoneForCausalLM"),
    "Exaone4ForCausalLM": ("exaone4", "Exaone4ForCausalLM"),
    "Fairseq2LlamaForCausalLM": ("fairseq2_llama", "Fairseq2LlamaForCausalLM"),
    "FalconForCausalLM": ("falcon", "FalconForCausalLM"),
    "FalconMambaForCausalLM": ("mamba", "MambaForCausalLM"),
    "FalconH1ForCausalLM": ("falcon_h1", "FalconH1ForCausalLM"),
    "FlexOlmoForCausalLM": ("flex_olmo", "FlexOlmoForCausalLM"),
    "GemmaForCausalLM": ("gemma", "GemmaForCausalLM"),
    "Gemma2ForCausalLM": ("gemma2", "Gemma2ForCausalLM"),
    "Gemma3ForCausalLM": ("gemma3", "Gemma3ForCausalLM"),
    "Gemma3nForCausalLM": ("gemma3n", "Gemma3nForCausalLM"),
    "Qwen3NextForCausalLM": ("qwen3_next", "Qwen3NextForCausalLM"),
    "GlmForCausalLM": ("glm", "GlmForCausalLM"),
    "Glm4ForCausalLM": ("glm4", "Glm4ForCausalLM"),
    "Glm4MoeForCausalLM": ("glm4_moe", "Glm4MoeForCausalLM"),
    "GptOssForCausalLM": ("gpt_oss", "GptOssForCausalLM"),
    "GPT2LMHeadModel": ("gpt2", "GPT2LMHeadModel"),
    "GPTBigCodeForCausalLM": ("gpt_bigcode", "GPTBigCodeForCausalLM"),
    "GPTJForCausalLM": ("gpt_j", "GPTJForCausalLM"),
    "GPTNeoXForCausalLM": ("gpt_neox", "GPTNeoXForCausalLM"),
    "GraniteForCausalLM": ("granite", "GraniteForCausalLM"),
    "GraniteMoeForCausalLM": ("granitemoe", "GraniteMoeForCausalLM"),
    "GraniteMoeHybridForCausalLM": ("granitemoehybrid", "GraniteMoeHybridForCausalLM"),  # noqa: E501
    "GraniteMoeSharedForCausalLM": ("granitemoeshared", "GraniteMoeSharedForCausalLM"),  # noqa: E501
    "GritLM": ("gritlm", "GritLM"),
    "Grok1ModelForCausalLM": ("grok1", "Grok1ForCausalLM"),
    "HunYuanMoEV1ForCausalLM": ("hunyuan_v1", "HunYuanMoEV1ForCausalLM"),
    "HunYuanDenseV1ForCausalLM": ("hunyuan_v1", "HunYuanDenseV1ForCausalLM"),
    "HCXVisionForCausalLM": ("hyperclovax_vision", "HCXVisionForCausalLM"),
    "InternLMForCausalLM": ("llama", "LlamaForCausalLM"),
    "InternLM2ForCausalLM": ("internlm2", "InternLM2ForCausalLM"),
    "InternLM2VEForCausalLM": ("internlm2_ve", "InternLM2VEForCausalLM"),
    "InternLM3ForCausalLM": ("llama", "LlamaForCausalLM"),
    "JAISLMHeadModel": ("jais", "JAISLMHeadModel"),
    "JambaForCausalLM": ("jamba", "JambaForCausalLM"),
    "KimiLinearForCausalLM": ("kimi_linear", "KimiLinearForCausalLM"),  # noqa: E501
    "Lfm2ForCausalLM": ("lfm2", "Lfm2ForCausalLM"),
    "Lfm2MoeForCausalLM": ("lfm2_moe", "Lfm2MoeForCausalLM"),
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
    "MistralForCausalLM": ("llama", "LlamaForCausalLM"),
    "MixtralForCausalLM": ("mixtral", "MixtralForCausalLM"),
    # transformers's mpt class has lower case
    "MptForCausalLM": ("mpt", "MPTForCausalLM"),
    "MPTForCausalLM": ("mpt", "MPTForCausalLM"),
    "MiMoForCausalLM": ("mimo", "MiMoForCausalLM"),
    "NemotronForCausalLM": ("nemotron", "NemotronForCausalLM"),
    "NemotronHForCausalLM": ("nemotron_h", "NemotronHForCausalLM"),
    "OlmoForCausalLM": ("olmo", "OlmoForCausalLM"),
    "Olmo2ForCausalLM": ("olmo2", "Olmo2ForCausalLM"),
    "Olmo3ForCausalLM": ("olmo2", "Olmo2ForCausalLM"),
    "OlmoeForCausalLM": ("olmoe", "OlmoeForCausalLM"),
    "OPTForCausalLM": ("opt", "OPTForCausalLM"),
    "OrionForCausalLM": ("orion", "OrionForCausalLM"),
    "OuroForCausalLM": ("ouro", "OuroForCausalLM"),
    "PanguEmbeddedForCausalLM": ("openpangu", "PanguEmbeddedForCausalLM"),
    "PanguUltraMoEForCausalLM": ("openpangu", "PanguUltraMoEForCausalLM"),
    "PersimmonForCausalLM": ("persimmon", "PersimmonForCausalLM"),
    "PhiForCausalLM": ("phi", "PhiForCausalLM"),
    "Phi3ForCausalLM": ("phi3", "Phi3ForCausalLM"),
    "PhiMoEForCausalLM": ("phimoe", "PhiMoEForCausalLM"),
    "Plamo2ForCausalLM": ("plamo2", "Plamo2ForCausalLM"),
    "QWenLMHeadModel": ("qwen", "QWenLMHeadModel"),
    "Qwen2ForCausalLM": ("qwen2", "Qwen2ForCausalLM"),
    "Qwen2MoeForCausalLM": ("qwen2_moe", "Qwen2MoeForCausalLM"),
    "Qwen3ForCausalLM": ("qwen3", "Qwen3ForCausalLM"),
    "Qwen3MoeForCausalLM": ("qwen3_moe", "Qwen3MoeForCausalLM"),
    "RWForCausalLM": ("falcon", "FalconForCausalLM"),
    "SeedOssForCausalLM": ("seed_oss", "SeedOssForCausalLM"),
    "Step3TextForCausalLM": ("step3_text", "Step3TextForCausalLM"),
    "StableLMEpochForCausalLM": ("stablelm", "StablelmForCausalLM"),
    "StableLmForCausalLM": ("stablelm", "StablelmForCausalLM"),
    "Starcoder2ForCausalLM": ("starcoder2", "Starcoder2ForCausalLM"),
    "SolarForCausalLM": ("solar", "SolarForCausalLM"),
    "TeleChat2ForCausalLM": ("telechat2", "TeleChat2ForCausalLM"),
    "TeleFLMForCausalLM": ("teleflm", "TeleFLMForCausalLM"),
    "XverseForCausalLM": ("llama", "LlamaForCausalLM"),
    "Zamba2ForCausalLM": ("zamba2", "Zamba2ForCausalLM"),
}

_EMBEDDING_MODELS = {
    # [Text-only]
    "BertModel": ("bert", "BertEmbeddingModel"),
    "BertSpladeSparseEmbeddingModel": ("bert", "BertSpladeSparseEmbeddingModel"),
    "DeciLMForCausalLM": ("nemotron_nas", "DeciLMForCausalLM"),
    "Gemma2Model": ("gemma2", "Gemma2ForCausalLM"),
    "Gemma3TextModel": ("gemma3", "Gemma3Model"),
    "GlmForCausalLM": ("glm", "GlmForCausalLM"),
    "GPT2ForSequenceClassification": ("gpt2", "GPT2ForSequenceClassification"),
    "GritLM": ("gritlm", "GritLM"),
    "GteModel": ("bert_with_rope", "SnowflakeGteNewModel"),
    "GteNewModel": ("bert_with_rope", "GteNewModel"),
    "InternLM2ForRewardModel": ("internlm2", "InternLM2ForRewardModel"),
    "JambaForSequenceClassification": ("jamba", "JambaForSequenceClassification"),  # noqa: E501
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
    "Qwen2ForRewardModel": ("qwen2_rm", "Qwen2ForRewardModel"),
    "Qwen2ForProcessRewardModel": ("qwen2_rm", "Qwen2ForProcessRewardModel"),
    "RobertaForMaskedLM": ("roberta", "RobertaEmbeddingModel"),
    "RobertaModel": ("roberta", "RobertaEmbeddingModel"),
    "TeleChat2ForCausalLM": ("telechat2", "TeleChat2ForCausalLM"),
    "XLMRobertaModel": ("roberta", "RobertaEmbeddingModel"),
    # [Multimodal]
    "CLIPModel": ("clip", "CLIPEmbeddingModel"),
    "LlavaNextForConditionalGeneration": (
        "llava_next",
        "LlavaNextForConditionalGeneration",
    ),
    "Phi3VForCausalLM": ("phi3v", "Phi3VForCausalLM"),
    "Qwen2VLForConditionalGeneration": ("qwen2_vl", "Qwen2VLForConditionalGeneration"),  # noqa: E501
    "SiglipModel": ("siglip", "SiglipEmbeddingModel"),
    # Technically Terratorch models work on images, both in
    # input and output. I am adding it here because it piggy-backs on embedding
    # models for the time being.
    "PrithviGeoSpatialMAE": ("terratorch", "Terratorch"),
    "Terratorch": ("terratorch", "Terratorch"),
}

_CROSS_ENCODER_MODELS = {
    "BertForSequenceClassification": ("bert", "BertForSequenceClassification"),
    "BertForTokenClassification": ("bert", "BertForTokenClassification"),
    "GteNewForSequenceClassification": (
        "bert_with_rope",
        "GteNewForSequenceClassification",
    ),
    "ModernBertForSequenceClassification": (
        "modernbert",
        "ModernBertForSequenceClassification",
    ),
    "ModernBertForTokenClassification": (
        "modernbert",
        "ModernBertForTokenClassification",
    ),
    "RobertaForSequenceClassification": ("roberta", "RobertaForSequenceClassification"),
    "XLMRobertaForSequenceClassification": (
        "roberta",
        "RobertaForSequenceClassification",
    ),
    # [Auto-converted (see adapters.py)]
    "JinaVLForRanking": ("jina_vl", "JinaVLForSequenceClassification"),  # noqa: E501,
}

_MULTIMODAL_MODELS = {
    # [Decoder-only]
    "AriaForConditionalGeneration": ("aria", "AriaForConditionalGeneration"),
    "AyaVisionForConditionalGeneration": (
        "aya_vision",
        "AyaVisionForConditionalGeneration",
    ),
    "BeeForConditionalGeneration": ("bee", "BeeForConditionalGeneration"),
    "Blip2ForConditionalGeneration": ("blip2", "Blip2ForConditionalGeneration"),
    "ChameleonForConditionalGeneration": (
        "chameleon",
        "ChameleonForConditionalGeneration",
    ),
    "Cohere2VisionForConditionalGeneration": (
        "cohere2_vision",
        "Cohere2VisionForConditionalGeneration",
    ),
    "DeepseekVLV2ForCausalLM": ("deepseek_vl2", "DeepseekVLV2ForCausalLM"),
    "DeepseekOCRForCausalLM": ("deepseek_ocr", "DeepseekOCRForCausalLM"),
    "DotsOCRForCausalLM": ("dots_ocr", "DotsOCRForCausalLM"),
    "Ernie4_5_VLMoeForConditionalGeneration": (
        "ernie45_vl",
        "Ernie4_5_VLMoeForConditionalGeneration",
    ),
    "FuyuForCausalLM": ("fuyu", "FuyuForCausalLM"),
    "Gemma3ForConditionalGeneration": ("gemma3_mm", "Gemma3ForConditionalGeneration"),  # noqa: E501
    "Gemma3nForConditionalGeneration": (
        "gemma3n_mm",
        "Gemma3nForConditionalGeneration",
    ),
    "GLM4VForCausalLM": ("glm4v", "GLM4VForCausalLM"),
    "Glm4vForConditionalGeneration": ("glm4_1v", "Glm4vForConditionalGeneration"),  # noqa: E501
    "Glm4vMoeForConditionalGeneration": ("glm4_1v", "Glm4vMoeForConditionalGeneration"),  # noqa: E501
    "GraniteSpeechForConditionalGeneration": (
        "granite_speech",
        "GraniteSpeechForConditionalGeneration",
    ),
    "H2OVLChatModel": ("h2ovl", "H2OVLChatModel"),
    "InternVLChatModel": ("internvl", "InternVLChatModel"),
    "NemotronH_Nano_VL_V2": ("nano_nemotron_vl", "NemotronH_Nano_VL_V2"),
    "InternS1ForConditionalGeneration": (
        "interns1",
        "InternS1ForConditionalGeneration",
    ),
    "InternVLForConditionalGeneration": (
        "interns1",
        "InternS1ForConditionalGeneration",
    ),
    "Idefics3ForConditionalGeneration": (
        "idefics3",
        "Idefics3ForConditionalGeneration",
    ),
    "SmolVLMForConditionalGeneration": ("smolvlm", "SmolVLMForConditionalGeneration"),  # noqa: E501
    "KeyeForConditionalGeneration": ("keye", "KeyeForConditionalGeneration"),
    "KeyeVL1_5ForConditionalGeneration": (
        "keye_vl1_5",
        "KeyeVL1_5ForConditionalGeneration",
    ),
    "RForConditionalGeneration": ("rvl", "RForConditionalGeneration"),
    "KimiVLForConditionalGeneration": ("kimi_vl", "KimiVLForConditionalGeneration"),  # noqa: E501
    "LightOnOCRForConditionalGeneration": (
        "lightonocr",
        "LightOnOCRForConditionalGeneration",
    ),
    "Llama_Nemotron_Nano_VL": ("nemotron_vl", "LlamaNemotronVLChatModel"),
    "Llama4ForConditionalGeneration": ("mllama4", "Llama4ForConditionalGeneration"),  # noqa: E501
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
    "MantisForConditionalGeneration": ("llava", "MantisForConditionalGeneration"),  # noqa: E501
    "MiDashengLMModel": ("midashenglm", "MiDashengLMModel"),
    "MiniMaxVL01ForConditionalGeneration": (
        "minimax_vl_01",
        "MiniMaxVL01ForConditionalGeneration",
    ),
    "MiniCPMO": ("minicpmo", "MiniCPMO"),
    "MiniCPMV": ("minicpmv", "MiniCPMV"),
    "Mistral3ForConditionalGeneration": (
        "mistral3",
        "Mistral3ForConditionalGeneration",
    ),
    "MolmoForCausalLM": ("molmo", "MolmoForCausalLM"),
    "NVLM_D": ("nvlm_d", "NVLM_D_Model"),
    "Ovis": ("ovis", "Ovis"),
    "Ovis2_5": ("ovis2_5", "Ovis2_5"),
    "PaddleOCRVLForConditionalGeneration": (
        "paddleocr_vl",
        "PaddleOCRVLForConditionalGeneration",
    ),
    "PaliGemmaForConditionalGeneration": (
        "paligemma",
        "PaliGemmaForConditionalGeneration",
    ),
    "Phi3VForCausalLM": ("phi3v", "Phi3VForCausalLM"),
    "Phi4MMForCausalLM": ("phi4mm", "Phi4MMForCausalLM"),
    "Phi4MultimodalForCausalLM": ("phi4_multimodal", "Phi4MultimodalForCausalLM"),  # noqa: E501
    "PixtralForConditionalGeneration": ("pixtral", "PixtralForConditionalGeneration"),  # noqa: E501
    "QwenVLForConditionalGeneration": ("qwen_vl", "QwenVLForConditionalGeneration"),  # noqa: E501
    "Qwen2VLForConditionalGeneration": ("qwen2_vl", "Qwen2VLForConditionalGeneration"),  # noqa: E501
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
    "Qwen3VLForConditionalGeneration": ("qwen3_vl", "Qwen3VLForConditionalGeneration"),  # noqa: E501
    "Qwen3VLMoeForConditionalGeneration": (
        "qwen3_vl_moe",
        "Qwen3VLMoeForConditionalGeneration",
    ),
    "SkyworkR1VChatModel": ("skyworkr1v", "SkyworkR1VChatModel"),
    "Step3VLForConditionalGeneration": ("step3_vl", "Step3VLForConditionalGeneration"),  # noqa: E501
    "TarsierForConditionalGeneration": ("tarsier", "TarsierForConditionalGeneration"),  # noqa: E501
    "Tarsier2ForConditionalGeneration": (
        "qwen2_vl",
        "Tarsier2ForConditionalGeneration",
    ),
    "UltravoxModel": ("ultravox", "UltravoxModel"),
    "VoxtralForConditionalGeneration": ("voxtral", "VoxtralForConditionalGeneration"),  # noqa: E501
    # [Encoder-decoder]
    "WhisperForConditionalGeneration": ("whisper", "WhisperForConditionalGeneration"),  # noqa: E501
}

_SPECULATIVE_DECODING_MODELS = {
    "MiMoMTPModel": ("mimo_mtp", "MiMoMTP"),
    "EagleLlamaForCausalLM": ("llama_eagle", "EagleLlamaForCausalLM"),
    "EagleLlama4ForCausalLM": ("llama4_eagle", "EagleLlama4ForCausalLM"),
    "EagleMiniCPMForCausalLM": ("minicpm_eagle", "EagleMiniCPMForCausalLM"),
    "Eagle3LlamaForCausalLM": ("llama_eagle3", "Eagle3LlamaForCausalLM"),
    "LlamaForCausalLMEagle3": ("llama_eagle3", "Eagle3LlamaForCausalLM"),
    "Eagle3Qwen2_5vlForCausalLM": ("llama_eagle3", "Eagle3LlamaForCausalLM"),
    "EagleDeepSeekMTPModel": ("deepseek_eagle", "EagleDeepseekV3ForCausalLM"),
    "DeepSeekMTPModel": ("deepseek_mtp", "DeepSeekMTP"),
    "ErnieMTPModel": ("ernie_mtp", "ErnieMTP"),
    "LongCatFlashMTPModel": ("longcat_flash_mtp", "LongCatFlashMTP"),
    "Glm4MoeMTPModel": ("glm4_moe_mtp", "Glm4MoeMTP"),
    "MedusaModel": ("medusa", "Medusa"),
    "OpenPanguMTPModel": ("openpangu_mtp", "OpenPanguMTP"),
    "Qwen3NextMTP": ("qwen3_next_mtp", "Qwen3NextMTP"),
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
    **_CROSS_ENCODER_MODELS,
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
