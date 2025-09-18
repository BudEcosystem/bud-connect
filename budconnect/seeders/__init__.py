from .engine import EngineSeeder
from .guardrails import GuardrailsSeeder
from .license import LicenseSeeder
from .litellm import LiteLLMSeeder as LiteLLMSeeder
from .model_details import ModelDetailsSeeder
from .tensorzero import TensorZeroSeeder
from .user import UserSeeder


seeders = {
    "user": UserSeeder,  # This should run first to create initial admin
    "engine": EngineSeeder,
    "license": LicenseSeeder,  # This should run before litellm and tensorzero
    # "litellm": LiteLLMSeeder,
    "tensorzero": TensorZeroSeeder,
    "model_details": ModelDetailsSeeder,  # This should run after litellm and tensorzero
    "guardrails": GuardrailsSeeder,  # This should run after tensorzero to ensure providers exist
}
