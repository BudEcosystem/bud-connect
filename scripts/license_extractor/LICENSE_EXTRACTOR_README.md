# License Extractor - Standalone Script

This standalone Python script extracts license information from a file or URL and enhances it using LLM analysis. It provides comprehensive license analysis with 22 predefined questions covering modification rights, distribution, commercial use, patents, and legal risks.

## Features

- **Multi-source Support**: Extract license text from local files (.txt, .md, .rst, .pdf) or URLs
- **Comprehensive Analysis**: 22 predefined questions covering all aspects of software licensing
- **Impact Assessment**: Each answer is evaluated for its impact on derivative work development
- **License Classification**: Categorizes licenses into 10 types with suitability ratings
- **Structured Output**: Saves results as JSON with detailed FAQ information

## Installation

Install the required dependencies:

```bash
pip install json-repair beautifulsoup4 PyPDF2 openai requests
```

## Configuration

Set the following environment variables:

```bash
export BUD_LLM_API_KEY="your-api-key-here"
export BUD_LLM_BASE_URL="https://api.openai.com/v1"  # Optional, defaults to OpenAI
export BUD_LLM_MODEL="gpt-4"  # Optional, defaults to gpt-4
```

## Usage

### Basic Usage

```bash
# Analyze a local license file
python license_extractor.py /path/to/LICENSE.txt

# Analyze a license from URL
python license_extractor.py https://example.com/license

# Specify custom output file
python license_extractor.py LICENSE.md --output my_analysis.json

# Enable verbose logging
python license_extractor.py LICENSE.txt --verbose
```

### Output

The script generates a JSON file containing:

- **License name and type**
- **Type description and suitability rating**
- **22 FAQs** with:
  - Question text
  - Answer (YES/NO)
  - Detailed reasoning
  - Impact assessment (POSITIVE/NEGATIVE/NEUTRAL)

### Example Output Structure

```json
{
  "name": "MIT License",
  "type": "Permissive Open Source",
  "type_description": "Allows modification and redistribution with minimal restrictions...",
  "type_suitability": "MOST",
  "faqs": [
    {
      "question": "Can you modify the software, model, or framework?",
      "answer": "YES",
      "reason": ["The MIT license explicitly grants permission to modify the software..."],
      "impact": "POSITIVE"
    }
    // ... 21 more questions
  ]
}
```

## License Types

The script categorizes licenses into 10 types with suitability ratings:

1. **Permissive Open Source** (MOST suitable)
2. **Copyleft Open Source** (GOOD)
3. **Weak Copyleft Open Source** (GOOD)
4. **Open Source but Restrictive** (LOW)
5. **Open Source but No Redistribution** (LOW)
6. **Non-Commercial License** (LOW)
7. **Fully Proprietary** (WORST)
8. **Proprietary with API Access** (WORST)
9. **Proprietary with Limited Customization** (LOW)
10. **Closed Source but Free to Use** (WORST)

## 22 Analysis Questions

The script analyzes each license against these comprehensive questions:

### Modification & Distribution
1. Can you modify the software, model, or framework?
2. Are there any restrictions on modifying core components?
3. Can you distribute the modified version of the software/model?
4. Are there limitations on how you share derivative works?
5. Must you open-source your modifications (Copyleft vs. Permissive)?

### Commercial Use
6. Are you allowed to monetize the tool you build on top of it?
7. Does the license restrict commercial applications?
8. Are there royalty requirements or revenue-sharing clauses?

### Attribution & Legal
9. Are you required to credit the original software, model, or tool?
10. Must you include license texts, disclaimers, or notices in your product?
11. Does the license require you to make your changes public?

### API & Usage Limits
12. If the tool provides API access, what are the usage limits?
13. Are you allowed to build commercial applications using the API?
14. Are there rate limits or paywalls for extended use?

### Patents & Legal Risks
15. Does the license provide any patent grants or protections?
16. Could you face legal risks if your tool extends the licensed software?
17. Are there restrictions on filing patents for derivative works?

### AI/Model Specific
18. If it's an AI model, does the license restrict how you can use the training data?
19. Are there privacy constraints that affect how user data is handled?

### Legal Protection
20. Can the licensor revoke your usage rights at any time?
21. Is there a clause that limits their liability in case of legal issues?
22. Are there terms that prevent the use of the tool for specific purposes?

## Error Handling

The script includes comprehensive error handling for:
- Missing or invalid license files/URLs
- Network connectivity issues
- API authentication problems
- JSON parsing errors
- File permission issues

## Supported File Types

- **Text files**: .txt, .md, .rst
- **PDF files**: .pdf
- **URLs**: Any web-accessible license content

## Based on BudModel License Extraction

This standalone script is based on the license extraction module from the BudModel microservice system, simplified for standalone use without database dependencies, MinIO storage, or HuggingFace-specific features.