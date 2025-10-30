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

import json
import logging
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

from budmicroframe.commons.exceptions import ClientException

from budconnect.commons.config import app_settings

from .manifest_builder import EvalManifestBuilder


logger = logging.getLogger(__name__)


class EvalService:
    """Service class for eval operations."""

    def __init__(self):
        """Initialize the eval service."""
        # Use configured output directory, relative to project root (base_dir)
        self.data_dir = app_settings.base_dir / app_settings.eval_output_dir

    async def build_manifest(
        self,
        output_filename: str = "eval_manifest.json",
        enable_analysis: bool = False,
        sample_size: Optional[int] = None
    ) -> Dict[str, Any]:
        """Build the eval manifest file.

        Args:
            output_filename: Name of the output file
            enable_analysis: Whether to enable LLM-based dataset analysis
            sample_size: Number of samples to extract per dataset (overrides EVAL_SAMPLE_SIZE env var)

        Returns:
            dict: Result of the build process with status, file path, counts
        """
        logger.info(
            f"Building eval manifest: {output_filename} "
            f"(analysis={enable_analysis}, sample_size={sample_size or app_settings.eval_sample_size})"
        )

        # Construct output path
        output_path = str(self.data_dir / output_filename)

        # Build the manifest
        builder = EvalManifestBuilder(
            output_path=output_path,
            enable_analysis=enable_analysis,
            sample_size=sample_size
        )
        result = await builder.run()

        logger.info(f"Manifest build completed: {result}")
        return result

    def get_manifest(self, version: Optional[str] = None) -> Dict[str, Any]:
        """Get manifest file by version.

        Args:
            version: Optional version number (e.g., "1.0.5"). If None, returns latest.

        Returns:
            dict: Manifest content

        Raises:
            ClientException: If version not found or file doesn't exist
        """
        if version:
            # Get specific version
            manifest_file = self.data_dir / f"eval_manifest-{version}.json"
            if not manifest_file.exists():
                raise ClientException(
                    message=f"Manifest version {version} not found",
                    status_code=404
                )
        else:
            # Get latest version (follow symlink)
            manifest_file = self.data_dir / "eval_manifest.json"
            if not manifest_file.exists():
                raise ClientException(
                    message="No manifest file found. Please build the manifest first.",
                    status_code=404
                )

            # Resolve symlink to get actual file
            if manifest_file.is_symlink():
                manifest_file = manifest_file.resolve()

        logger.info(f"Reading manifest from: {manifest_file}")

        try:
            with open(manifest_file, 'r', encoding='utf-8') as f:
                manifest_data = json.load(f)
            return manifest_data
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse manifest JSON: {e}")
            raise ClientException(
                message="Failed to parse manifest file",
                status_code=500
            )
        except Exception as e:
            logger.error(f"Failed to read manifest: {e}")
            raise ClientException(
                message="Failed to read manifest file",
                status_code=500
            )

    def list_available_versions(self) -> Dict[str, Any]:
        """List all available manifest versions.

        Returns:
            dict: Available versions with latest version info
        """
        # Find all versioned manifest files
        manifest_files = list(self.data_dir.glob("eval_manifest-*.json"))

        versions = []
        for file in manifest_files:
            # Extract version from filename (eval_manifest-1.0.5.json -> 1.0.5)
            version = file.stem.replace("eval_manifest-", "")
            versions.append(version)

        # Sort versions (semantic versioning)
        def version_key(v: str) -> tuple:
            """Convert version string to tuple for sorting."""
            try:
                return tuple(map(int, v.split('.')))
            except (ValueError, AttributeError):
                return (0, 0, 0)

        versions.sort(key=version_key)

        # Get latest version
        latest_version = versions[-1] if versions else None

        # If no versions found but symlink exists, try to get version from it
        if not versions:
            symlink_file = self.data_dir / "eval_manifest.json"
            if symlink_file.exists():
                try:
                    with open(symlink_file, 'r') as f:
                        data = json.load(f)
                        latest_version = data.get("manifest_version", "unknown")
                        versions = [latest_version]
                except Exception:
                    pass

        return {
            "latest_version": latest_version or "none",
            "available_versions": versions,
            "total_count": len(versions)
        }
