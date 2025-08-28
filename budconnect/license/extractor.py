"""License Extraction Module.

This module provides functionality to extract and analyze license information
from various sources (URLs, files, text) using LLM analysis.
"""

import json
import logging
import re
from typing import Any, Dict
from urllib.request import ProxyHandler, Request, build_opener

from bs4 import BeautifulSoup
from json_repair import repair_json
from openai import AsyncOpenAI
from PyPDF2 import PdfReader


logger = logging.getLogger(__name__)


class LicenseExtractionException(Exception):
    """Custom exception for license extraction errors."""

    pass


# License Analysis Prompt
LICENSE_ANALYSIS_PROMPT = """
Act as an expert License reviewer. Your goal is to carefully analyse the given software/model license agreement and answer the questions given below in the form of a JSON. Ensure that all the answers for the questions are only based on the license given below, do not assume anything - ONLY USE THE DETAILS GIVEN. Don't infer on anything outside from what is given on the provided license. Also, Ensure that the JSON created is written inside the tags <json> </json>
The JSON should be structurally correct and exact without any error, comments, code etc.
Name of the license (key: name) - Name of the license as provided on the license.
Type of the license (key: type) - Type of the license, Pick from the list given here - [Permissive Open Source, Copyleft Open Source, Weak Copyleft Open Source, Open Source but Restrictive, Open Source but No Redistribution, Non-Commercial License, Fully Proprietary, Proprietary with API Access, Proprietary with Limited Customization, Closed Source but Free to Use]
Following questions with a dictionary for each questions (key: Q1, Q2 etc):
For example: {question: Question under consideration, answer: YES or NO, reason: List[String] : List of strings}
Q1. Can you modify the software, model, or framework? : Analyse if the software, model etc are opensource and can be modified for building a derivative software (Yes or No) and reasons.
Q2. Are there any restrictions on modifying core components? : Analyse if the software/model source code and all the components could be modified with out any restrictions (Yes or No) and reasons.
Q3. Can you distribute the modified version of the software/model? : Analyse if the model could be finetuned/trained/modified and distributed or if the software could be modified and distributed without any restrictions (Yes or No) and reasons.
Q4. Are there limitations on how you share derivative works? : Analyse if there are any limitations in sharing the derivate model or software, like attributions, following the same license type, etc. (Yes or No) and reasons.
Q5. Must you open-source your modifications (Copyleft vs. Permissive)? :  (Yes or No) and reasons
Q6. Are you allowed to monetize the tool you build on top of it? : (Yes or No) and reasons.
Q7. Does the license restrict commercial applications (e.g., Non-Commercial License)? (Yes or no) and reasons
Q8. Are there royalty requirements or revenue-sharing clauses? (Yes or No) and reasons
Q9. Are you required to credit the original software, model, or tool? (Yes or No) and reasons
Q10. Must you include license texts, disclaimers, or notices in your product? (Yes or No) and reasons
Q11. Does the license require you to make your changes public? (Yes or No) and reasons
Q12. If the tool provides API access, what are the usage limits? (Yes or No) and reasons
Q13. Are you allowed to build commercial applications using the API? (Yes or No) and reasons
Q14. Are there rate limits or paywalls for extended use? (Yes or No) and reasons.
Q15. Does the license provide any patent grants or protections? (Yes or No) and reasons.
Q16. Could you face legal risks if your tool extends the licensed software? (Yes or No) and reasons.
Q17. Are there restrictions on filing patents for derivative works? (Yes or No) and reasons.
Q18. If it's an AI model, does the license restrict how you can use the training data? (Yes or No) and reasons
Q19. Are there privacy constraints that affect how user data is handled? (Yes or No) and reasons.
Q20. Can the licensor revoke your usage rights at any time? (Yes or No) and reasons.
Q21. Is there a clause that limits their liability in case of legal issues? (Yes or No) and reasons.
Q22. Are there terms that prevent the use of the tool for specific purposes (e.g., ethical AI clauses)? (Yes or No) and reasons.
"""

# License Questions with Impact Assessment
LICENSE_QUESTIONS = {
    "Q1": {"question": "Can you modify the software, model, or framework?", "impact": "POSITIVE"},
    "Q2": {"question": "Are there any restrictions on modifying core components?", "impact": "NEGATIVE"},
    "Q3": {"question": "Can you distribute the modified version of the software/model?", "impact": "POSITIVE"},
    "Q4": {"question": "Are there limitations on how you share derivative works?", "impact": "NEGATIVE"},
    "Q5": {"question": "Must you open-source your modifications (Copyleft vs. Permissive)?", "impact": "NEGATIVE"},
    "Q6": {"question": "Are you allowed to monetize the tool you build on top of it?", "impact": "POSITIVE"},
    "Q7": {"question": "Does the license restrict commercial applications?", "impact": "NEGATIVE"},
    "Q8": {"question": "Are there royalty requirements or revenue-sharing clauses?", "impact": "NEGATIVE"},
    "Q9": {"question": "Are you required to credit the original software, model, or tool?", "impact": "NEGATIVE"},
    "Q10": {
        "question": "Must you include license texts, disclaimers, or notices in your product?",
        "impact": "NEGATIVE",
    },
    "Q11": {"question": "Does the license require you to make your changes public?", "impact": "NEGATIVE"},
    "Q12": {"question": "If the tool provides API access, what are the usage limits?", "impact": "NEGATIVE"},
    "Q13": {"question": "Are you allowed to build commercial applications using the API?", "impact": "POSITIVE"},
    "Q14": {"question": "Are there rate limits or paywalls for extended use?", "impact": "NEGATIVE"},
    "Q15": {"question": "Does the license provide any patent grants or protections?", "impact": "POSITIVE"},
    "Q16": {
        "question": "Could you face legal risks if your tool extends the licensed software?",
        "impact": "NEGATIVE",
    },
    "Q17": {"question": "Are there restrictions on filing patents for derivative works?", "impact": "NEGATIVE"},
    "Q18": {
        "question": "If it's an AI model, does the license restrict how you can use the training data?",
        "impact": "NEGATIVE",
    },
    "Q19": {"question": "Are there privacy constraints that affect how user data is handled?", "impact": "NEGATIVE"},
    "Q20": {"question": "Can the licensor revoke your usage rights at any time?", "impact": "NEGATIVE"},
    "Q21": {
        "question": "Is there a clause that limits their liability in case of legal issues?",
        "impact": "NEGATIVE",
    },
    "Q22": {
        "question": "Are there terms that prevent the use of the tool for specific purposes?",
        "impact": "NEGATIVE",
    },
}

# License Type Definitions
LICENSE_TYPES = [
    {
        "type": "Permissive Open Source",
        "description": "Allows modification and redistribution with minimal restrictions, usually requiring only attribution.",
        "suitability": "MOST",
    },
    {
        "type": "Copyleft Open Source",
        "description": "Requires derivative works to be distributed under the same license terms.",
        "suitability": "GOOD",
    },
    {
        "type": "Weak Copyleft Open Source",
        "description": "Allows linking with proprietary software but requires modifications to the library itself to be open-sourced.",
        "suitability": "GOOD",
    },
    {
        "type": "Open Source but Restrictive",
        "description": "Open source with significant restrictions on usage or distribution.",
        "suitability": "LOW",
    },
    {
        "type": "Open Source but No Redistribution",
        "description": "Source code is available but redistribution is not permitted.",
        "suitability": "LOW",
    },
    {
        "type": "Non-Commercial License",
        "description": "Restricts commercial use while allowing non-commercial modifications.",
        "suitability": "LOW",
    },
    {
        "type": "Fully Proprietary",
        "description": "Users cannot modify, distribute, or access the source code; typically requires a paid license.",
        "suitability": "WORST",
    },
    {
        "type": "Proprietary with API Access",
        "description": "Proprietary software that provides API access for integration.",
        "suitability": "WORST",
    },
    {
        "type": "Proprietary with Limited Customization",
        "description": "Proprietary software with some customization options but no source code access.",
        "suitability": "LOW",
    },
    {
        "type": "Closed Source but Free to Use",
        "description": "Free to use but source code is not available.",
        "suitability": "WORST",
    },
]


def get_url_content(url: str) -> str:
    """Fetch license content from a URL."""
    try:
        # Set up proxy handler
        proxy_handler = ProxyHandler({})
        opener = build_opener(proxy_handler)

        # Create request with headers
        req = Request(url, headers={"User-Agent": "Mozilla/5.0"})

        # Fetch content
        response = opener.open(req)
        html = response.read().decode("utf-8")

        # Parse HTML
        soup = BeautifulSoup(html, "html.parser")
        license_content = str(soup.text).strip()

        if not license_content:
            raise LicenseExtractionException(f"Unable to get license text from URL: {url}")

        return license_content
    except Exception as e:
        logger.error(f"Error fetching license content from URL: {url} - {e}")
        raise LicenseExtractionException(f"Unable to fetch content from URL: {url}") from e


def get_text_content(text: str) -> str:
    """Process raw text content."""
    if not text or text.strip() == "":
        raise LicenseExtractionException("License text is empty")
    return text.strip()


def get_pdf_content(pdf_bytes: bytes) -> str:
    """Extract text from PDF bytes."""
    try:
        import io

        pdf_text = []
        pdf_file = io.BytesIO(pdf_bytes)
        reader = PdfReader(pdf_file)
        for page in reader.pages:
            pdf_text.append(page.extract_text())
        return "\n".join(pdf_text)
    except Exception as e:
        logger.error(f"Error reading PDF content: {e}")
        raise LicenseExtractionException("Unable to read PDF content") from e


def extract_json_from_string(response_text: str) -> str:
    """Extract JSON content from the LLM response text."""
    try:
        # Look for JSON within <json> tags first
        json_pattern = r"<json>(.*?)</json>"
        match = re.search(json_pattern, response_text, re.DOTALL)
        if match:
            return match.group(1).strip()

        # Fallback: look for any JSON-like structure
        json_pattern = r"\{.*\}"
        match = re.search(json_pattern, response_text, re.DOTALL)
        if match:
            return match.group()

        logger.warning("No JSON found in response, returning original text")
        return response_text
    except Exception as e:
        logger.error(f"Error extracting JSON from response: {e}")
        return response_text


async def generate_license_details(
    license_text: str,
    api_key: str,
    base_url: str = "https://api.openai.com/v1",
    model: str = "gpt-4",
    timeout: int = 120,
) -> Dict[str, Any]:
    """Generate license details from the license text using LLM analysis."""
    if not license_text:
        raise LicenseExtractionException("License content is empty")

    if not api_key:
        raise LicenseExtractionException("LLM API key is required for license extraction")

    try:
        # Initialize AsyncOpenAI client with configurable timeout for LLM calls
        client = AsyncOpenAI(api_key=api_key, base_url=base_url, timeout=float(timeout))

        logger.info(f"Sending license text to LLM for analysis (timeout: {timeout}s)...")
        response = await client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": LICENSE_ANALYSIS_PROMPT},
                {"role": "user", "content": license_text},
            ],
            temperature=0.1,
            timeout=float(timeout),
        )

        llm_response = response.choices[0].message.content
        logger.debug("LLM response received")

        # Extract JSON from response
        json_str = extract_json_from_string(llm_response)

        # Parse and repair JSON if needed
        try:
            llm_response = json.loads(json_str)
        except json.JSONDecodeError:
            logger.warning("Initial JSON parsing failed, attempting repair...")
            repaired_json = repair_json(json_str)
            llm_response = json.loads(repaired_json)

        # Process the response
        answers = {}
        answers["name"] = llm_response.get("name", "Unknown")
        answers["type"] = llm_response.get("type", "Unknown")
        answers["type_description"] = ""
        answers["type_suitability"] = ""
        answers["faqs"] = []

        # Find matching license type information
        for license_type in LICENSE_TYPES:
            if license_type["type"].lower() == answers["type"].lower():
                answers["type_description"] = license_type["description"]
                answers["type_suitability"] = license_type["suitability"]
                break

        # Process FAQ answers
        for k, v in llm_response.items():
            if k.upper() in LICENSE_QUESTIONS:
                faq_item = {}

                # Set default impact as NEUTRAL
                impact = "NEUTRAL"

                # Get the expected impact from license questions
                expected_impact = LICENSE_QUESTIONS[k.upper()]["impact"]

                # Determine actual impact based on answer
                if v.get("answer", "").lower() == "yes":
                    impact = expected_impact
                elif v.get("answer", "").lower() == "no":
                    impact = "POSITIVE" if expected_impact == "NEGATIVE" else "NEGATIVE"

                # Build FAQ item
                faq_item["question"] = v.get("question", LICENSE_QUESTIONS[k.upper()]["question"])
                faq_item["answer"] = v.get("answer", "")
                faq_item["reason"] = (
                    v.get("reason", []) if isinstance(v.get("reason"), list) else [v.get("reason", "")]
                )
                faq_item["impact"] = impact

                answers["faqs"].append(faq_item)

        return answers

    except Exception as e:
        logger.error(f"Error generating license FAQ: {e}")
        raise LicenseExtractionException("Extracting license details failed") from e


async def extract_license_from_source(
    source_type: str,
    source: str,
    api_key: str,
    base_url: str = "https://api.openai.com/v1",
    model: str = "gpt-4",
    timeout: int = 120,
) -> Dict[str, Any]:
    """Extract license information from various sources.

    Args:
        source_type: Type of source - "url", "text", or "pdf_base64"
        source: The source content (URL, text, or base64 PDF)
        api_key: API key for the LLM service
        base_url: Base URL for the LLM API
        model: Model name to use

    Returns:
        Dictionary with extracted license details
    """
    # Get license content based on source type
    if source_type == "url":
        license_content = get_url_content(source)
    elif source_type == "text":
        license_content = get_text_content(source)
    elif source_type == "pdf_base64":
        import base64

        pdf_bytes = base64.b64decode(source)
        license_content = get_pdf_content(pdf_bytes)
    else:
        raise LicenseExtractionException(f"Invalid source type: {source_type}")

    # Generate license details using LLM
    return await generate_license_details(license_content, api_key, base_url, model, timeout)
