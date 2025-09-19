import logging
import re
from typing import List, Optional, Tuple
from uuid import UUID

from budmicroframe.commons.exceptions import ClientException

from budconnect.commons.config import app_settings
from budconnect.model.crud import LicenseCRUD
from budconnect.model.models import License

from .extractor import LicenseExtractionException, extract_license_from_source
from .schemas import (
    LicenseCreate,
    LicenseExtractRequest,
    LicenseExtractResponse,
    LicenseFAQ,
    LicenseUpdate,
)


logger = logging.getLogger(__name__)


class LicenseService:
    @staticmethod
    def get_all_licenses(page: int = 1, page_size: int = 100) -> Tuple[List[License], int]:
        """Get all licenses with pagination.

        Args:
            page: Page number (starts from 1)
            page_size: Number of items per page

        Returns:
            Tuple of (list of licenses, total count)
        """
        with LicenseCRUD() as crud:
            offset = (page - 1) * page_size
            # Get all licenses to count total
            all_licenses_result = crud.fetch_many()
            # Handle tuple return from fetch_many
            if isinstance(all_licenses_result, tuple):
                all_licenses = all_licenses_result[0] if all_licenses_result else []
            else:
                all_licenses = all_licenses_result if all_licenses_result else []

            total = len(all_licenses)

            # Get paginated results
            licenses_result = crud.fetch_many(offset=offset, limit=page_size)
            # Handle tuple return from fetch_many
            if isinstance(licenses_result, tuple):
                licenses = licenses_result[0] if licenses_result else []
            else:
                licenses = licenses_result if licenses_result else []

            return licenses, total

    @staticmethod
    def get_license_by_id(license_id: UUID) -> License:
        """Get a license by its ID.

        Args:
            license_id: UUID of the license

        Returns:
            License object

        Raises:
            ClientException: If license not found
        """
        with LicenseCRUD() as crud:
            license = crud.fetch_one(conditions={"id": license_id})
            if not license:
                raise ClientException(f"License with ID {license_id} not found")
            return license  # type: ignore

    @staticmethod
    def get_license_by_key(key: str) -> License:
        """Get a license by its key.

        Args:
            key: Key identifier of the license

        Returns:
            License object

        Raises:
            ClientException: If license not found
        """
        with LicenseCRUD() as crud:
            # Use fetch_many to search by key
            licenses_result = crud.fetch_many()
            # Handle tuple return
            if isinstance(licenses_result, tuple):
                licenses = licenses_result[0] if licenses_result else []
            else:
                licenses = licenses_result if licenses_result else []

            # Find license by key
            for license in licenses:
                if license.key == key:
                    return license  # type: ignore

            raise ClientException(f"License with key '{key}' not found")

    @staticmethod
    def create_license(license_data: LicenseCreate) -> License:
        """Create a new license.

        Args:
            license_data: License creation data

        Returns:
            Created license object

        Raises:
            ClientException: If license with same key already exists
        """
        with LicenseCRUD() as crud:
            # Check if license with same key exists
            licenses_result = crud.fetch_many()
            if isinstance(licenses_result, tuple):
                licenses = licenses_result[0] if licenses_result else []
            else:
                licenses = licenses_result if licenses_result else []

            for license in licenses:
                if license.key == license_data.key:
                    raise ClientException(f"License with key '{license_data.key}' already exists")

            # Create the license using upsert
            license_dict = license_data.model_dump()
            # Generate a new UUID for the license
            from uuid import uuid4

            license_dict["id"] = uuid4()
            license_id = crud.upsert(license_dict)
            result = crud.fetch_one(conditions={"id": license_id})
            return result  # type: ignore

    @staticmethod
    def update_license(license_id: UUID, license_data: LicenseUpdate) -> License:
        """Update an existing license.

        Args:
            license_id: UUID of the license to update
            license_data: Update data

        Returns:
            Updated license object

        Raises:
            ClientException: If license not found
            ClientException: If trying to update key to an existing one
        """
        with LicenseCRUD() as crud:
            # Check if license exists
            existing = crud.fetch_one(conditions={"id": license_id})
            if not existing:
                raise ClientException(f"License with ID {license_id} not found")

            # If updating key, check for conflicts
            update_dict = license_data.model_dump(exclude_unset=True)
            if "key" in update_dict and update_dict["key"] != existing.key:
                # Check all licenses for conflict
                licenses_result = crud.fetch_many()
                if isinstance(licenses_result, tuple):
                    licenses = licenses_result[0] if licenses_result else []
                else:
                    licenses = licenses_result if licenses_result else []

                for license in licenses:
                    if license.key == update_dict["key"]:
                        raise ClientException(f"License with key '{update_dict['key']}' already exists")

            # Update the license using upsert
            # Merge existing data with updates
            merged_data = {
                "id": license_id,
                "key": existing.key,
                "name": existing.name,
                "type": existing.type,
                "type_description": existing.type_description,
                "type_suitability": existing.type_suitability,
                "faqs": existing.faqs,
            }
            merged_data.update(update_dict)
            crud.upsert(merged_data, conflict_target=["id"])
            result = crud.fetch_one(conditions={"id": license_id})
            return result  # type: ignore

    @staticmethod
    def delete_license(license_id: UUID) -> bool:
        """Delete a license.

        Args:
            license_id: UUID of the license to delete

        Returns:
            True if deleted successfully

        Raises:
            ClientException: If license not found
        """
        with LicenseCRUD() as crud:
            # Check if license exists
            existing = crud.fetch_one(conditions={"id": license_id})
            if not existing:
                raise ClientException(f"License with ID {license_id} not found")

            # Delete the license using raw SQL since CRUD doesn't have delete
            from sqlalchemy import delete

            from budconnect.model.models import License

            session = crud.get_session()
            try:
                stmt = delete(License).where(License.id == license_id)
                session.execute(stmt)
                session.commit()
                return True
            finally:
                crud.cleanup_session(session)

    @staticmethod
    def search_licenses(
        license_type: Optional[str] = None, suitability: Optional[str] = None, search_term: Optional[str] = None
    ) -> List[License]:
        """Search licenses by various criteria.

        Args:
            license_type: Filter by license type
            suitability: Filter by suitability rating
            search_term: Search in name and key

        Returns:
            List of matching licenses
        """
        with LicenseCRUD() as crud:
            conditions = {}
            if license_type:
                conditions["type"] = license_type
            if suitability:
                conditions["type_suitability"] = suitability

            licenses_result = crud.fetch_many(conditions=conditions)
            # Handle tuple return from fetch_many
            if isinstance(licenses_result, tuple):
                licenses = licenses_result[0] if licenses_result else []
            else:
                licenses = licenses_result if licenses_result else []

            # Filter by search term if provided
            if search_term:
                search_lower = search_term.lower()
                licenses = [l for l in licenses if search_lower in l.key.lower() or search_lower in l.name.lower()]

            return licenses

    @staticmethod
    def generate_license_key(license_name: str) -> str:
        """Generate a license key from the license name.

        Args:
            license_name: Name of the license

        Returns:
            Generated license key
        """
        # Remove special characters and convert to lowercase
        key = re.sub(r"[^a-zA-Z0-9\s\-_.]", "", license_name.lower())
        # Replace spaces with hyphens
        key = re.sub(r"\s+", "-", key)
        # Remove duplicate hyphens
        key = re.sub(r"-+", "-", key)
        # Remove leading/trailing hyphens
        key = key.strip("-")

        return key if key else "unknown-license"

    @staticmethod
    async def extract_license(request: LicenseExtractRequest) -> LicenseExtractResponse:
        """Extract license information from a source.

        Args:
            request: License extraction request

        Returns:
            Extracted license information

        Raises:
            ClientException: If extraction fails or API key is missing
        """
        # Check if API key is configured
        api_key = app_settings.llm_api_key
        if not api_key:
            raise ClientException(
                "License extraction requires LLM API key. Please configure BUD_LLM_API_KEY environment variable."
            )

        try:
            # Extract license details with configurable timeout
            extracted = await extract_license_from_source(
                source_type=request.source_type,
                source=request.source,
                api_key=api_key,
                base_url=app_settings.llm_base_url,
                model=app_settings.llm_model,
                timeout=app_settings.llm_timeout,
            )

            # Generate or use provided key
            if request.key:
                license_key = request.key
            else:
                license_key = LicenseService.generate_license_key(extracted.get("name", "Unknown"))

            # Convert FAQs to schema format
            faqs = []
            for faq in extracted.get("faqs", []):
                faqs.append(
                    LicenseFAQ(
                        question=faq.get("question", ""),
                        answer=faq.get("answer", ""),
                        reason=faq.get("reason", []),
                        impact=faq.get("impact", "NEUTRAL"),
                    )
                )

            # Create response
            return LicenseExtractResponse(
                key=license_key,
                name=extracted.get("name", "Unknown License"),
                type=extracted.get("type", "Unknown"),
                type_description=extracted.get("type_description", ""),
                type_suitability=extracted.get("type_suitability", "UNKNOWN"),
                faqs=faqs,
                extraction_metadata={"source_type": request.source_type, "model_used": app_settings.llm_model},
            )

        except LicenseExtractionException as e:
            logger.error(f"License extraction failed: {e}")
            raise ClientException(f"Failed to extract license: {str(e)}") from e
        except TimeoutError as e:
            logger.error(f"License extraction timed out after {app_settings.llm_timeout}s: {e}")
            raise ClientException(
                f"License extraction timed out after {app_settings.llm_timeout} seconds. "
                f"The LLM service may be slow. Please try again later or increase BUD_LLM_TIMEOUT."
            ) from e
        except Exception as e:
            logger.error(f"Unexpected error during license extraction: {e}")
            # Check if it's a timeout-related error from httpx or openai
            error_str = str(e).lower()
            if "timeout" in error_str or "timed out" in error_str or "readtimeout" in error_str:
                logger.error(f"Detected timeout error: {e}")
                raise ClientException(
                    f"License extraction timed out after {app_settings.llm_timeout} seconds. "
                    f"The LLM service may be slow. Please try again later or increase BUD_LLM_TIMEOUT."
                ) from e
            raise ClientException(f"Unexpected error during license extraction: {str(e)}") from e

    @staticmethod
    async def extract_and_create_license(request: LicenseExtractRequest) -> License:
        """Extract license information and create a new license record.

        Args:
            request: License extraction request

        Returns:
            Created license object

        Raises:
            ClientException: If extraction fails or license already exists
        """
        # Extract license information
        extracted = await LicenseService.extract_license(request)

        # Check if license with same key already exists
        with LicenseCRUD() as crud:
            licenses_result = crud.fetch_many()
            if isinstance(licenses_result, tuple):
                licenses = licenses_result[0] if licenses_result else []
            else:
                licenses = licenses_result if licenses_result else []

            for license in licenses:
                if license.key == extracted.key:
                    raise ClientException(f"License with key '{extracted.key}' already exists")

            # Create the license
            license_data = LicenseCreate(
                key=extracted.key,
                name=extracted.name,
                type=extracted.type,
                type_description=extracted.type_description,
                type_suitability=extracted.type_suitability,
                faqs=[faq.model_dump() for faq in extracted.faqs],
            )

            from uuid import uuid4

            license_dict = license_data.model_dump()
            license_dict["id"] = uuid4()
            license_id = crud.upsert(license_dict)
            result = crud.fetch_one(conditions={"id": license_id})
            return result  # type: ignore
