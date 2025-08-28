from typing import Optional
from uuid import UUID

from budmicroframe.commons import logging
from budmicroframe.commons.exceptions import ClientException
from fastapi import APIRouter, HTTPException, Query, status

from .schemas import (
    LicenseCreate,
    LicenseExtractRequest,
    LicenseListResponse,
    LicenseResponse,
    LicenseUpdate,
)
from .services import LicenseService


logger = logging.get_logger(__name__)

license_router = APIRouter(prefix="/licenses", tags=["License"])


@license_router.get("/")
async def get_licenses(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(100, ge=1, le=500, description="Number of items per page"),
    license_type: Optional[str] = Query(None, description="Filter by license type"),
    suitability: Optional[str] = Query(None, description="Filter by suitability rating"),
    search: Optional[str] = Query(None, description="Search in license name and key"),
):
    """Get all licenses with optional filtering and pagination.

    Args:
        page: Page number (starts from 1)
        page_size: Number of items per page
        license_type: Optional filter by license type
        suitability: Optional filter by suitability rating (MOST, GOOD, LOW, WORST)
        search: Optional search term to filter by name or key

    Returns:
        List of licenses with pagination info
    """
    try:
        if search or license_type or suitability:
            licenses = LicenseService.search_licenses(
                license_type=license_type, suitability=suitability, search_term=search
            )
            # Apply pagination to search results
            start_idx = (page - 1) * page_size
            end_idx = start_idx + page_size
            paginated_licenses = licenses[start_idx:end_idx]
            total = len(licenses)
        else:
            paginated_licenses, total = LicenseService.get_all_licenses(page, page_size)

        logger.info(f"Got {len(paginated_licenses)} licenses, type: {type(paginated_licenses)}")
        if paginated_licenses:
            logger.info(f"First item type: {type(paginated_licenses[0])}")

        license_responses = []
        for license in paginated_licenses:
            license_dict = {
                "id": license.id,
                "key": license.key,
                "name": license.name,
                "type": license.type,
                "type_description": license.type_description,
                "type_suitability": license.type_suitability,
                "faqs": license.faqs if license.faqs else [],
            }
            license_responses.append(LicenseResponse(**license_dict))

        return LicenseListResponse(licenses=license_responses, total=total, page=page, page_size=page_size)
    except Exception as e:
        logger.error(f"Error fetching licenses: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@license_router.get("/{license_id}")
async def get_license(license_id: UUID):
    """Get a specific license by ID.

    Args:
        license_id: UUID of the license

    Returns:
        License details
    """
    try:
        license = LicenseService.get_license_by_id(license_id)
        return LicenseResponse(
            id=license.id,
            key=license.key,
            name=license.name,
            type=license.type,
            type_description=license.type_description,
            type_suitability=license.type_suitability,
            faqs=license.faqs if license.faqs else [],
        )
    except ClientException as e:
        if "not found" in str(e).lower():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error fetching license {license_id}: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@license_router.get("/key/{key}")
async def get_license_by_key(key: str):
    """Get a specific license by its key identifier.

    Args:
        key: Key identifier of the license (e.g., 'apache-2.0', 'mit')

    Returns:
        License details
    """
    try:
        license = LicenseService.get_license_by_key(key)
        return LicenseResponse(
            id=license.id,
            key=license.key,
            name=license.name,
            type=license.type,
            type_description=license.type_description,
            type_suitability=license.type_suitability,
            faqs=license.faqs if license.faqs else [],
        )
    except ClientException as e:
        if "not found" in str(e).lower():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error fetching license with key {key}: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@license_router.post("/", status_code=status.HTTP_201_CREATED)
async def create_license(license_data: LicenseCreate):
    """Create a new license.

    Args:
        license_data: License creation data

    Returns:
        Created license details
    """
    try:
        license = LicenseService.create_license(license_data)
        return LicenseResponse(
            id=license.id,
            key=license.key,
            name=license.name,
            type=license.type,
            type_description=license.type_description,
            type_suitability=license.type_suitability,
            faqs=license.faqs if license.faqs else [],
        )
    except ClientException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating license: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@license_router.patch("/{license_id}")
async def update_license(license_id: UUID, license_data: LicenseUpdate):
    """Update an existing license.

    Args:
        license_id: UUID of the license to update
        license_data: Update data (only provided fields will be updated)

    Returns:
        Updated license details
    """
    try:
        license = LicenseService.update_license(license_id, license_data)
        return LicenseResponse(
            id=license.id,
            key=license.key,
            name=license.name,
            type=license.type,
            type_description=license.type_description,
            type_suitability=license.type_suitability,
            faqs=license.faqs if license.faqs else [],
        )
    except ClientException as e:
        if "not found" in str(e).lower():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except ClientException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error updating license {license_id}: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@license_router.delete("/{license_id}")
async def delete_license(license_id: UUID):
    """Delete a license.

    Args:
        license_id: UUID of the license to delete

    Returns:
        No content on success
    """
    try:
        LicenseService.delete_license(license_id)
        return {"message": "License deleted successfully"}
    except ClientException as e:
        if "not found" in str(e).lower():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error deleting license {license_id}: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@license_router.post("/extract")
async def extract_license(request: LicenseExtractRequest):
    """Extract license information from a source without creating a record.

    This endpoint analyzes license content from various sources (URL, text, PDF)
    and returns structured license information including type classification,
    suitability rating, and comprehensive FAQ analysis.

    Args:
        request: License extraction request with source information

    Returns:
        Extracted license information with analysis
    """
    try:
        extracted = await LicenseService.extract_license(request)
        return extracted
    except ClientException as e:
        logger.error(f"License extraction failed: {str(e)}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error during license extraction: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@license_router.post("/extract-and-create", status_code=status.HTTP_201_CREATED)
async def extract_and_create_license(request: LicenseExtractRequest):
    """Extract license information from a source and create a new license record.

    This endpoint combines extraction and creation in a single operation.
    It analyzes the license content and immediately creates a database record
    with the extracted information.

    Args:
        request: License extraction request with source information

    Returns:
        Created license details
    """
    try:
        license = await LicenseService.extract_and_create_license(request)
        return LicenseResponse(
            id=license.id,
            key=license.key,
            name=license.name,
            type=license.type,
            type_description=license.type_description,
            type_suitability=license.type_suitability,
            faqs=license.faqs if license.faqs else [],
        )
    except ClientException as e:
        logger.error(f"License extraction and creation failed: {str(e)}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error during license extraction and creation: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
