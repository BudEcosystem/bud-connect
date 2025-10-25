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

"""Data collector for eval module - makes API calls and aggregates data into JSON."""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, cast

import httpx


logger = logging.getLogger(__name__)


class EvalDataCollector:
    """Collects data from multiple API endpoints and creates JSON files."""

    def __init__(self, output_dir: str = "cache/eval_data") -> None:
        """Initialize the data collector.

        Args:
            output_dir: Directory to store generated JSON files
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.client = httpx.AsyncClient(timeout=30.0)

    async def fetch_data_from_api(self, url: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Fetch data from a single API endpoint.

        Args:
            url: API endpoint URL
            params: Optional query parameters

        Returns:
            Dict: Response data from the API
        """
        try:
            logger.info(f"Fetching data from: {url}")
            response = await self.client.get(url, params=params)
            response.raise_for_status()
            return cast(Dict[str, Any], response.json())
        except Exception as e:
            logger.error(f"Failed to fetch data from {url}: {e}")
            return {"error": str(e), "url": url}

    async def collect_data_from_endpoints(self, endpoints: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Collect data from multiple API endpoints.

        Args:
            endpoints: List of endpoint configurations with 'url' and optional 'params' and 'key'

        Returns:
            Dict: Aggregated data from all endpoints
        """
        data_dict: Dict[str, Any] = {}
        collected_data: Dict[str, Any] = {
            "collection_timestamp": datetime.utcnow().isoformat(),
            "endpoints_count": len(endpoints),
            "data": data_dict,
        }

        for endpoint_config in endpoints:
            url = endpoint_config.get("url")
            params = endpoint_config.get("params")
            key = endpoint_config.get("key", url)

            if not url:
                logger.warning(f"Skipping endpoint with no URL: {endpoint_config}")
                continue

            # Ensure key is a string (use url as fallback)
            key_str = key if isinstance(key, str) else url
            if not key_str:
                logger.warning(f"Skipping endpoint with no valid key: {endpoint_config}")
                continue

            data = await self.fetch_data_from_api(url, params)
            data_dict[key_str] = data

        return collected_data

    async def save_to_json(self, data: Dict[str, Any], filename: str) -> Path:
        """Save collected data to a JSON file.

        Args:
            data: Data to save
            filename: Output filename (will be saved in output_dir)

        Returns:
            Path: Path to the saved file
        """
        output_path = self.output_dir / filename
        try:
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, sort_keys=True)
            logger.info(f"Successfully saved data to: {output_path}")
            return output_path
        except Exception as e:
            logger.error(f"Failed to save data to {output_path}: {e}")
            raise

    async def run_collection(self, endpoints: List[Dict[str, Any]], output_filename: str) -> Dict[str, Any]:
        """Run the complete data collection process.

        Args:
            endpoints: List of endpoint configurations
            output_filename: Name of the output JSON file

        Returns:
            Dict: Summary of the collection process
        """
        try:
            logger.info(f"Starting data collection from {len(endpoints)} endpoints")

            # Collect data from all endpoints
            collected_data = await self.collect_data_from_endpoints(endpoints)

            # Save to JSON file
            output_path = await self.save_to_json(collected_data, output_filename)

            summary = {
                "status": "success",
                "endpoints_processed": len(endpoints),
                "output_file": str(output_path),
                "timestamp": collected_data["collection_timestamp"],
            }

            logger.info(f"Data collection completed successfully: {summary}")
            return summary

        except Exception as e:
            logger.exception(f"Data collection failed: {e}")
            return {
                "status": "failed",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat(),
            }
        finally:
            await self.client.aclose()
