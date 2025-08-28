from .engine import EngineSeeder
from .license import LicenseSeeder
from .litellm import LiteLLMSeeder as LiteLLMSeeder
from .model_details import ModelDetailsSeeder
from .tensorzero import TensorZeroSeeder


seeders = {
    "engine": EngineSeeder,
    "license": LicenseSeeder,  # This should run before litellm and tensorzero
    # "litellm": LiteLLMSeeder,
    "tensorzero": TensorZeroSeeder,
    "model_details": ModelDetailsSeeder,  # This should run after litellm and tensorzero
}
