"""Which vLLM parsers ``EngineService.get_compatible_engines`` hands to a deployment.

budsim copies ``tool_calling_parser_type`` from this endpoint into the simulation and budcluster
passes it to vLLM as ``--tool-call-parser`` unchanged, so a wrong value here is a runtime that
returns every tool call as plain text. That is how Qwen3-Coder ended up on ``hermes``: its
``qwen3_xml`` rule was only consulted after the ``Qwen3MoeForCausalLM`` default had already
answered.

The resolver runs against the shipped seed data -- vLLM parser rules from ``engines.json`` and
architecture defaults from ``model_architectures.json`` -- with the database calls faked out.
"""

import json
import pathlib
import uuid
from types import SimpleNamespace
from typing import Any, Dict, List, Optional

import pytest

import budconnect.commons  # noqa: F401  # loads the ORM models in an order that avoids a circular import
from budconnect.engine import services
from budconnect.engine.schemas import CompatibleEngine, DeviceArchitecture, ParserMatchType, ParserRuleType


DATA_DIR = pathlib.Path(__file__).parent.parent / "budconnect" / "seeders" / "data"
ENGINE_ID = uuid.uuid4()


def _vllm_rules() -> List[SimpleNamespace]:
    engines = json.loads((DATA_DIR / "engines.json").read_text())
    vllm = next(engine for engine in engines if engine["name"] == "vllm")
    return [
        SimpleNamespace(
            id=uuid.uuid5(uuid.NAMESPACE_URL, f"{rule['rule_type']}:{rule['pattern']}"),
            engine_id=ENGINE_ID,
            rule_type=ParserRuleType(rule["rule_type"]),
            parser_type=rule["parser_type"],
            match_type=ParserMatchType(rule["match_type"]),
            pattern=rule["pattern"],
            priority=rule.get("priority", 0),
            enabled=rule.get("enabled", True),
            notes=rule.get("notes"),
            chat_template=rule.get("chat_template"),
        )
        for rule in vllm["parser_rules"]
    ]


def _architectures() -> Dict[str, SimpleNamespace]:
    data = json.loads((DATA_DIR / "model_architectures.json").read_text())
    return {arch["class_name"]: SimpleNamespace(**arch) for arch in data["architectures"]}


class _FakeCRUD:
    """Stands in for every CRUD the resolver opens, answering from seed data instead of the database."""

    def __init__(self, architecture: str, model_info: Optional[SimpleNamespace]) -> None:
        self.architecture = architecture
        self.model_info = model_info
        self.architectures = _architectures()
        self.rules = _vllm_rules()
        self.session = None

    def __call__(self) -> "_FakeCRUD":
        return self

    def __enter__(self) -> "_FakeCRUD":
        return self

    def __exit__(self, *exc: Any) -> bool:
        return False

    def get_by_uri_with_architecture(self, uri: str, session: Any = None) -> Optional[tuple]:
        if self.model_info is None:
            return None
        return self.model_info, self.architectures[self.architecture]

    def get_by_class_name(self, class_name: str, session: Any = None) -> Optional[SimpleNamespace]:
        return self.architectures.get(class_name)

    def get_compatible_engines(self, *args: Any, **kwargs: Any) -> List[CompatibleEngine]:
        return [
            CompatibleEngine(
                engine="vllm",
                device_architecture=DeviceArchitecture.CUDA,
                version="test",
                container_image="test",
                engine_id=ENGINE_ID,
            )
        ]

    def get_rules_for_engines(self, engine_ids: List[uuid.UUID], session: Any = None) -> Dict[uuid.UUID, list]:
        return {ENGINE_ID: self.rules}


def _resolve(
    monkeypatch: pytest.MonkeyPatch,
    model_uri: str,
    architecture: str,
    model_info: Optional[SimpleNamespace] = None,
) -> CompatibleEngine:
    fake = _FakeCRUD(architecture, model_info)
    for name in ("ModelInfoCRUD", "ModelArchitectureClassCRUD", "EngineCRUD", "EngineParserRuleCRUD"):
        monkeypatch.setattr(services, name, fake)
    (engine,) = services.EngineService.get_compatible_engines(
        model_architecture=architecture,
        device_architecture=DeviceArchitecture.CUDA,
        engine_version="test",
        engine="vllm",
        model_uri=model_uri,
    )
    return engine


@pytest.mark.parametrize(
    ("model_uri", "architecture", "tool_parser", "reasoning_parser", "source"),
    [
        # Qwen3.5-architecture checkpoints (Qwen3.5 through Qwen3.8) emit <tool_call><function=...> XML.
        ("Qwen/Qwen3.8-27B", "Qwen3_5ForConditionalGeneration", "qwen3_coder", "qwen3", "architecture_default"),
        (
            "Qwen/Qwen3.5-122B-A10B",
            "Qwen3_5MoeForConditionalGeneration",
            "qwen3_coder",
            "qwen3",
            "architecture_default",
        ),
        # A rule names a family that shares its architecture with models using another format.
        ("Qwen/Qwen3-Coder-30B-A3B-Instruct", "Qwen3MoeForCausalLM", "qwen3_xml", "qwen3", "engine_parser_rule"),
        ("moonshotai/Kimi-K2-Thinking", "DeepseekV3ForCausalLM", "kimi_k2", "kimi_k2", "engine_parser_rule"),
        # kimi_k2 reasoning starts inside a thought, so the non-thinking Instruct keeps deepseek_v3, which
        # passes text through unless thinking is requested.
        ("moonshotai/Kimi-K2-Instruct", "DeepseekV3ForCausalLM", "kimi_k2", "deepseek_v3", "engine_parser_rule"),
        ("NousResearch/Hermes-3-Llama-3.1-8B", "LlamaForCausalLM", "hermes", None, "engine_parser_rule"),
        ("deepseek-ai/DeepSeek-R1-0528", "DeepseekV3ForCausalLM", "deepseek_v3", "deepseek_r1", "engine_parser_rule"),
        # No rule matches: the architecture default still applies.
        ("Qwen/Qwen3-8B", "Qwen3ForCausalLM", "hermes", "qwen3", "architecture_default"),
    ],
)
def test_rule_beats_architecture_default(
    monkeypatch: pytest.MonkeyPatch,
    model_uri: str,
    architecture: str,
    tool_parser: str,
    reasoning_parser: Optional[str],
    source: str,
) -> None:
    """A rule matching the model URI is more specific than its architecture's default."""
    engine = _resolve(monkeypatch, model_uri, architecture)

    assert engine.tool_calling_parser_type == tool_parser
    assert engine.reasoning_parser_type == reasoning_parser
    assert engine.parser_source == source


def test_model_info_beats_rule_and_architecture_default(monkeypatch: pytest.MonkeyPatch) -> None:
    """A parser set on the model itself is the most specific answer and wins outright."""
    model_info = SimpleNamespace(tool_calling_parser_type="pythonic", endpoints=[], chat_template=None)

    engine = _resolve(monkeypatch, "Qwen/Qwen3-Coder-30B-A3B-Instruct", "Qwen3MoeForCausalLM", model_info)

    assert engine.tool_calling_parser_type == "pythonic"
    assert engine.parser_source == "model_default"
