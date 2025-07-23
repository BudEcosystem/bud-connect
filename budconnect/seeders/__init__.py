from .engine import EngineSeeder
from .litellm import LiteLLMSeeder as LiteLLMSeeder
from .model_details import ModelDetailsSeeder
from .tensorzero import TensorZeroSeeder


seeders = {
    "engine": EngineSeeder,
    # "litellm": LiteLLMSeeder,
    "tensorzero": TensorZeroSeeder,
    "model_details": ModelDetailsSeeder,  # This should run after litellm and tensorzero
}
