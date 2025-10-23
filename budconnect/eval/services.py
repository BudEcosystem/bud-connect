#  -----------------------------------------------------------------------------
#  Copyright (c) 2024 Bud Ecosystem Inc.
#  #
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#  #
#      http://www.apache.org/licenses/LICENSE-2.0
#  #
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#  -----------------------------------------------------------------------------

"""Eval service layer - contains business logic for eval operations."""

import logging
from pathlib import Path
from typing import Any, Dict

from .manifest_builder import EvalManifestBuilder


logger = logging.getLogger(__name__)


class EvalService:
    """Service class for eval operations."""

    async def build_manifest(
        self, output_filename: str = "eval_manifest.json", enable_analysis: bool = False
    ) -> Dict[str, Any]:
        """Build the eval manifest file.

        Args:
            output_filename: Name of the output file
            enable_analysis: Whether to enable LLM-based dataset analysis

        Returns:
            dict: Result of the build process with status, file path, counts
        """
        logger.info(f"Building eval manifest: {output_filename} (analysis={enable_analysis})")

        # Construct output path
        eval_data_dir = Path(__file__).parent / "data"
        output_path = str(eval_data_dir / output_filename)

        # Build the manifest
        builder = EvalManifestBuilder(output_path=output_path, enable_analysis=enable_analysis)
        result = await builder.run()

        logger.info(f"Manifest build completed: {result}")
        return result
