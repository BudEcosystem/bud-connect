#!/usr/bin/env python3
"""Standalone License Extraction Script

This script extracts license information from a file or URL and enhances it
using LLM analysis. It provides comprehensive license analysis with 22
predefined questions covering modification rights, distribution, commercial use,
patents, and legal risks.

Usage:
    python license_extractor.py /path/to/LICENSE.txt
    python license_extractor.py https://example.com/license

Environment Variables:
    BUD_LLM_BASE_URL: OpenAI-compatible API endpoint
    BUD_LLM_API_KEY: API key for the LLM service
    BUD_LLM_MODEL: Model name (default: gpt-4)
"""

import argparse
import json
import logging
import os
import re
from pathlib import Path
from typing import Any, Dict
from urllib.request import ProxyHandler, Request, build_opener

from bs4 import BeautifulSoup
from json_repair import repair_json
from openai import OpenAI
from PyPDF2 import PdfReader


# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


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
Q10. 	Must you include license texts, disclaimers, or notices in your product? (Yes or No) and reasons
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
    "Q5": {
        "question": "Must you open-source your modifications (Copyleft vs. Permissive)?",
        "impact": "NEGATIVE",
    },
    "Q6": {"question": "Are you allowed to monetize the tool you build on top of it?", "impact": "POSITIVE"},
    "Q7": {
        "question": "Does the license restrict commercial applications (e.g., Non-Commercial License)?",
        "impact": "NEGATIVE",
    },
    "Q8": {"question": "Are there royalty requirements or revenue-sharing clauses?", "impact": "NEGATIVE"},
    "Q9": {
        "question": "Are you required to credit the original software, model, or tool?",
        "impact": "NEGATIVE",
    },
    "Q10": {
        "question": "Must you include license texts, disclaimers, or notices in your product?",
        "impact": "NEGATIVE",
    },
    "Q11": {"question": "Does the license require you to make your changes public?", "impact": "NEGATIVE"},
    "Q12": {"question": "If the tool provides API access, what are the usage limits?", "impact": "NEGATIVE"},
    "Q13": {
        "question": "Are you allowed to build commercial applications using the API?",
        "impact": "POSITIVE",
    },
    "Q14": {"question": "Are there rate limits or paywalls for extended use?", "impact": "NEGATIVE"},
    "Q15": {"question": "Does the license provide any patent grants or protections?", "impact": "POSITIVE"},
    "Q16": {
        "question": "Could you face legal risks if your tool extends the licensed software?",
        "impact": "NEGATIVE",
    },
    "Q17": {
        "question": "Are there restrictions on filing patents for derivative works?",
        "impact": "NEGATIVE",
    },
    "Q18": {
        "question": "If it's an AI model, does the license restrict how you can use the training data?",
        "impact": "NEGATIVE",
    },
    "Q19": {
        "question": "Are there privacy constraints that affect how user data is handled?",
        "impact": "NEGATIVE",
    },
    "Q20": {"question": "Can the licensor revoke your usage rights at any time?", "impact": "NEGATIVE"},
    "Q21": {
        "question": "Is there a clause that limits their liability in case of legal issues?",
        "impact": "NEGATIVE",
    },
    "Q22": {
        "question": "Are there terms that prevent the use of the tool for specific purposes (e.g., ethical AI clauses)?",
        "impact": "NEGATIVE",
    },
}

# License Types with Suitability
LICENSE_TYPES = [
    {
        "type": "Permissive Open Source",
        "description": "Allows modification and redistribution with minimal restrictions, usually requiring only attribution.",
        "suitability": "MOST",
    },
    {
        "type": "Copyleft Open Source",
        "description": "Requires any modifications or derivative works to be shared under the same license terms.",
        "suitability": "GOOD",
    },
    {
        "type": "Weak Copyleft Open Source",
        "description": "Allows linking with proprietary software, but modifications to the open-source parts must remain open.",
        "suitability": "GOOD",
    },
    {
        "type": "Open Source but Restrictive",
        "description": "Allows modification but places restrictions such as non-commercial use or additional compliance requirements.",
        "suitability": "LOW",
    },
    {
        "type": "Open Source but No Redistribution",
        "description": "Allows modifications for personal use but prohibits sharing or distributing modified versions.",
        "suitability": "LOW",
    },
    {
        "type": "Non-Commercial License",
        "description": "The software can be modified and shared, but only for personal or educational use. Commercial distribution is prohibited.",
        "suitability": "LOW",
    },
    {
        "type": "Fully Proprietary",
        "description": "Users cannot modify, distribute, or access the source code; typically requires a paid license.",
        "suitability": "WORST",
    },
    {
        "type": "Proprietary with API Access",
        "description": "Source code remains closed, but users can integrate with the software via an API.",
        "suitability": "WORST",
    },
    {
        "type": "Proprietary with Limited Customization",
        "description": "Some modifications are allowed but only within defined boundaries set by the licensor.",
        "suitability": "LOW",
    },
    {
        "type": "Closed Source but Free to Use",
        "description": "Users can access and use the software without cost but cannot modify or distribute it.",
        "suitability": "WORST",
    },
]


class LicenseExtractionException(Exception):
    """Custom exception for license extraction errors."""

    pass


def get_url_content(url: str) -> str:
    """Fetch and return the text content from a URL."""
    try:
        req = Request(url=url, headers={"User-Agent": "Mozilla/5.0"})
        opener = build_opener(ProxyHandler({}))
        with opener.open(req, timeout=10) as response:
            content = response.read()

        soup = BeautifulSoup(content, "html.parser")
        license_content = str(soup.text).strip()
        if not license_content:
            raise LicenseExtractionException(f"Unable to get license text from given url: {url}")
        return license_content
    except Exception as e:
        logger.error(f"Error fetching license content from url: {url} - {e}")
        raise LicenseExtractionException(f"Unable to fetch content from URL: {url}") from e


def get_text_file_content(file_path: str) -> str:
    """Read and return the content of a text or markdown file."""
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            return file.read()
    except FileNotFoundError:
        logger.error(f"File not found: {file_path}")
        raise LicenseExtractionException(f"The specified file does not exist: {file_path}")
    except PermissionError:
        logger.error(f"Permission denied for file: {file_path}")
        raise LicenseExtractionException(f"Permission denied while accessing the file: {file_path}")
    except Exception as e:
        logger.error(f"Error reading text file: {e}")
        raise LicenseExtractionException(f"Unable to read the text file: {file_path}") from e


def get_pdf_file_content(file_path: str) -> str:
    """Read and return the text content from a PDF file."""
    try:
        pdf_text = []
        with open(file_path, "rb") as pdf_file:
            reader = PdfReader(pdf_file)
            for page in reader.pages:
                pdf_text.append(page.extract_text())
        return "\n".join(pdf_text)
    except FileNotFoundError:
        logger.error(f"File not found: {file_path}")
        raise LicenseExtractionException(f"The specified PDF file does not exist: {file_path}")
    except PermissionError:
        logger.error(f"Permission denied for file: {file_path}")
        raise LicenseExtractionException(f"Permission denied while accessing the PDF file: {file_path}")
    except Exception as e:
        logger.error(f"Error reading PDF file: {e}")
        raise LicenseExtractionException(f"Unable to read the PDF file: {file_path}") from e


def get_license_content_from_source(source: str) -> str:
    """Get license content from a given source (URL or file path)."""
    try:
        content = None
        if source.startswith(("http://", "https://")):
            # Fetch content from URL
            content = get_url_content(source)
        elif os.path.isfile(source):
            # Fetch content from a file
            file_extension = Path(source).suffix.lower()
            if file_extension in [".txt", ".md", ".rst", ""]:
                content = get_text_file_content(source)
            elif file_extension == ".pdf":
                content = get_pdf_file_content(source)
            else:
                logger.error(f"Unsupported file type: {file_extension}")
                raise LicenseExtractionException(f"Unsupported file type: {file_extension}")
        else:
            logger.error(f"Invalid source provided: {source}")
            raise LicenseExtractionException(f"Invalid source provided: {source}")

        if not content or content.strip() == "":
            raise LicenseExtractionException("License content is empty")

        return content
    except LicenseExtractionException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error fetching license content: {e}")
        raise LicenseExtractionException("Unexpected error fetching license content") from e


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


def generate_license_details(license_text: str, client: OpenAI, model: str) -> Dict[str, Any]:
    """Generate license details from the license text using LLM analysis."""
    if not license_text:
        logger.error("License content is None or empty.")
        raise LicenseExtractionException("License content is empty.")

    try:
        logger.info("Sending license text to LLM for analysis...")
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": LICENSE_ANALYSIS_PROMPT},
                {"role": "user", "content": license_text},
            ],
            temperature=0.1,
        )

        llm_response = response.choices[0].message.content
        logger.debug(f"LLM response: {llm_response}")

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
        answers["faqs"] = {}

        # Find matching license type information
        for license_type in LICENSE_TYPES:
            if license_type["type"].lower() == answers["type"].lower():
                answers["type_description"] = license_type["description"]
                answers["type_suitability"] = license_type["suitability"]
                break

        # Process FAQ answers
        for k, v in llm_response.items():
            if k.upper() in LICENSE_QUESTIONS:
                # Initialize the dictionary for this question if it doesn't exist
                answers["faqs"][k] = {}

                # Set default impact as NEUTRAL
                impact = "NEUTRAL"

                # Get the expected impact from license questions
                expected_impact = LICENSE_QUESTIONS[k.upper()]["impact"]

                # Determine actual impact based on answer
                if v.get("answer", "").lower() == "yes":
                    impact = expected_impact
                elif v.get("answer", "").lower() == "no":
                    impact = "POSITIVE" if expected_impact == "NEGATIVE" else "NEGATIVE"

                # Safely assign values using get() to avoid KeyError
                answers["faqs"][k]["impact"] = impact
                answers["faqs"][k]["answer"] = v.get("answer", "")
                answers["faqs"][k]["question"] = v.get("question", LICENSE_QUESTIONS[k.upper()]["question"])
                answers["faqs"][k]["reason"] = v.get("reason", "")

        # Convert answers to a list of dictionaries for compatibility
        reformatted_faqs = []
        for _k, v in answers["faqs"].items():
            reformatted_faqs.append(v)
        answers["faqs"] = reformatted_faqs

        return answers

    except Exception as e:
        logger.error(f"Error generating license FAQ: {e}")
        raise LicenseExtractionException("Extracting license details failed") from e


def save_license_analysis(analysis: Dict[str, Any], output_file: str) -> None:
    """Save the license analysis to a JSON file."""
    try:
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(analysis, f, indent=2, ensure_ascii=False)
        logger.info(f"License analysis saved to: {output_file}")
    except Exception as e:
        logger.error(f"Error saving analysis to file: {e}")
        raise LicenseExtractionException(f"Failed to save analysis to {output_file}") from e


def get_config_from_env() -> Dict[str, str]:
    """Get LLM configuration from environment variables."""
    base_url = os.getenv("BUD_LLM_BASE_URL", "https://api.openai.com/v1")
    api_key = os.getenv("BUD_LLM_API_KEY")
    model = os.getenv("BUD_LLM_MODEL", "qwen3-32b")

    if not api_key:
        raise LicenseExtractionException(
            "BUD_LLM_API_KEY environment variable is required. "
            "Please set it to your OpenAI API key or compatible service API key."
        )

    return {"base_url": base_url, "api_key": api_key, "model": model}


def generate_output_filename(input_source: str) -> str:
    """Generate output filename based on input source."""
    if input_source.startswith(("http://", "https://")):
        # For URLs, use a simple filename
        return "license_analysis.json"
    else:
        # For files, use the input filename
        input_path = Path(input_source)
        return f"{input_path.stem}_analysis.json"


def main():
    """Main function to handle CLI arguments and orchestrate license extraction."""
    parser = argparse.ArgumentParser(
        description="Extract and enhance license information from a file or URL",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python license_extractor.py /path/to/LICENSE.txt
  python license_extractor.py https://example.com/license
  python license_extractor.py LICENSE.md --output custom_analysis.json

Environment Variables:
  BUD_LLM_BASE_URL: OpenAI-compatible API endpoint (default: https://api.openai.com/v1)
  BUD_LLM_API_KEY: API key for the LLM service (required)
  BUD_LLM_MODEL: Model name (default: gpt-4)
        """,
    )

    parser.add_argument("source", help="License file path or URL to analyze")

    parser.add_argument("--output", "-o", help="Output JSON file path (default: auto-generated based on input)")

    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose logging")

    args = parser.parse_args()

    # Configure logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    try:
        # Get configuration from environment
        config = get_config_from_env()
        logger.info(f"Using model: {config['model']}")
        logger.info(f"Using base URL: {config['base_url']}")

        # Initialize OpenAI client
        client = OpenAI(base_url=config["base_url"], api_key=config["api_key"])

        # Extract license content
        logger.info(f"Extracting license content from: {args.source}")
        license_content = get_license_content_from_source(args.source)
        logger.info(f"Successfully extracted {len(license_content)} characters of license content")

        # Generate license analysis
        analysis = generate_license_details(license_content, client, config["model"])

        # Determine output filename
        output_file = args.output or generate_output_filename(args.source)

        # Save analysis
        save_license_analysis(analysis, output_file)

        # Print summary
        print(f"\n{'='*60}")
        print("LICENSE ANALYSIS COMPLETE")
        print(f"{'='*60}")
        print(f"License Name: {analysis.get('name', 'Unknown')}")
        print(f"License Type: {analysis.get('type', 'Unknown')}")
        print(f"Suitability: {analysis.get('type_suitability', 'Unknown')}")
        print(f"Total FAQs: {len(analysis.get('faqs', []))}")
        print(f"Output saved to: {output_file}")
        print(f"{'='*60}")

    except LicenseExtractionException as e:
        logger.error(f"License extraction failed: {e}")
        print(f"Error: {e}")
        exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        print(f"Unexpected error: {e}")
        exit(1)


if __name__ == "__main__":
    main()
