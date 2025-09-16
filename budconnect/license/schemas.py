from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field, field_validator


class LicenseFAQ(BaseModel):
    question: str
    answer: str
    reason: Optional[List[str]] = Field(default=None, description="Reasoning for the answer")
    impact: Optional[str] = Field(default="NEUTRAL", description="Impact assessment: POSITIVE, NEGATIVE, or NEUTRAL")


class LicenseBase(BaseModel):
    key: str = Field(..., description="Unique key identifier for the license")
    name: str = Field(..., description="Human-readable name of the license")
    type: str = Field(..., description="Classification of the license type")
    type_description: str = Field(..., description="Detailed description of the license type")
    type_suitability: str = Field(..., description="Suitability rating (MOST, GOOD, LOW, WORST)")
    faqs: List[LicenseFAQ] = Field(default_factory=list, description="List of FAQs about the license")


class LicenseCreate(LicenseBase):
    pass


class LicenseUpdate(BaseModel):
    key: Optional[str] = Field(None, description="Unique key identifier for the license")
    name: Optional[str] = Field(None, description="Human-readable name of the license")
    type: Optional[str] = Field(None, description="Classification of the license type")
    type_description: Optional[str] = Field(None, description="Detailed description of the license type")
    type_suitability: Optional[str] = Field(None, description="Suitability rating")
    faqs: Optional[List[LicenseFAQ]] = Field(None, description="List of FAQs about the license")


class LicenseResponse(LicenseBase):
    id: UUID = Field(..., description="Unique identifier for the license")

    class Config:
        """Pydantic model configuration."""

        from_attributes = True


class LicenseListResponse(BaseModel):
    licenses: List[LicenseResponse]
    total: int = Field(..., description="Total number of licenses")
    page: int = Field(..., description="Current page number")
    page_size: int = Field(..., description="Number of items per page")


class LicenseExtractRequest(BaseModel):
    source_type: str = Field(
        ..., description="Type of source: 'url', 'text', or 'pdf_base64'", pattern="^(url|text|pdf_base64)$"
    )
    source: str = Field(..., description="The source content (URL, raw text, or base64-encoded PDF)")
    key: Optional[str] = Field(None, description="Optional custom key for the license")

    @field_validator("source")
    def validate_source(cls, v: str, values: Optional[Dict[str, Any]] = None) -> str:
        """Validate that source is not empty."""
        if not v or v.strip() == "":
            raise ValueError("Source cannot be empty")
        return v


class LicenseExtractResponse(BaseModel):
    key: Optional[str] = Field(None, description="Suggested or provided license key")
    name: str = Field(..., description="Extracted license name")
    type: str = Field(..., description="License type classification")
    type_description: str = Field(..., description="Description of the license type")
    type_suitability: str = Field(..., description="Suitability rating")
    faqs: List[LicenseFAQ] = Field(default_factory=list, description="Extracted FAQs with analysis")
    extraction_metadata: Optional[Dict[str, Any]] = Field(None, description="Metadata about the extraction process")
