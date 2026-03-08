"""
OpenAI Document Analysis Module
Sends extracted text to OpenAI for summarization, metadata extraction, and risk detection.
"""

import json
import os
from typing import Any

from openai import OpenAI


def get_client() -> OpenAI:
    """Create an OpenAI client using the API key from environment."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key or api_key == "your-openai-api-key-here":
        raise ValueError(
            "OPENAI_API_KEY is not set. Please configure it in the .env file."
        )
    return OpenAI(api_key=api_key)


ANALYSIS_PROMPT = """You are a document intelligence assistant specializing in contract and legal document analysis.

Analyze the following document text and return a JSON object with these exact keys:

1. "summary": A high-level summary of the document (2-4 paragraphs).

2. "metadata": An object containing the following fields (use null if not found):
   - "document_type": Type of document/contract
   - "parties": List of parties involved (names and roles like buyer, seller, vendor, etc.)
   - "person_names": List of person names mentioned
   - "company_names": List of company/organization names
   - "effective_date": When the contract/agreement takes effect
   - "expiration_date": Expiration or renewal date
   - "contract_type": Specific type of contract (e.g., NDA, SLA, MSA, EULA, etc.)
   - "jurisdiction": Governing law or jurisdiction
   - "payment_terms": Payment terms summary
   - "termination_terms": Termination clause summary
   - "force_majeure": Force majeure clause summary
   - "liability_indemnity": Liability/indemnity clause summary
   - "confidentiality": Confidentiality obligations summary
   - "other_metadata": Any other important contract metadata detected (as an object)

3. "risks": A list of risk/alert objects, each containing:
   - "title": Short title of the risk (e.g., "Auto-Renewal Clause")
   - "severity": "High", "Medium", or "Low"
   - "quoted_text": The exact relevant text from the document
   - "explanation": Why this is important or risky
   - "category": One of: "Termination", "Force Majeure", "Auto-Renewal", "Penalty", "Indemnification", "Liability Limitation", "Exclusivity", "Non-Compete", "Non-Solicitation", "Unusual Obligation", "Missing Terms", "Ambiguous Language", "Red Flag", "Other"

4. "important_clauses": A list of important clause objects, each containing:
   - "title": Clause title
   - "quoted_text": The relevant text
   - "significance": Brief explanation of why it matters

Return ONLY valid JSON. No markdown, no code fences, no explanatory text outside the JSON.

DOCUMENT TEXT:
{text}
"""


def analyze_document(text: str, filename: str) -> dict[str, Any]:
    """
    Send extracted text to OpenAI for comprehensive analysis.
    Returns a dict with summary, metadata, risks, and important_clauses.
    """
    client = get_client()

    # Truncate very long documents to fit within context limits
    max_chars = 100_000
    truncated = False
    if len(text) > max_chars:
        text = text[:max_chars]
        truncated = True

    prompt = ANALYSIS_PROMPT.format(text=text)

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": "You are a precise document analysis assistant. Always respond with valid JSON only.",
            },
            {"role": "user", "content": prompt},
        ],
        temperature=0.1,
        max_tokens=8000,
    )

    raw = response.choices[0].message.content.strip()

    # Clean up potential markdown code fences
    if raw.startswith("```"):
        raw = raw.split("\n", 1)[1] if "\n" in raw else raw[3:]
    if raw.endswith("```"):
        raw = raw[:-3]
    if raw.startswith("json"):
        raw = raw[4:]
    raw = raw.strip()

    try:
        result = json.loads(raw)
    except json.JSONDecodeError:
        result = {
            "summary": raw,
            "metadata": {},
            "risks": [],
            "important_clauses": [],
            "_parse_error": "Could not parse OpenAI response as JSON. Raw response included as summary.",
        }

    if truncated:
        result["_note"] = "Document was truncated to 100,000 characters for analysis."

    result["_filename"] = filename
    return result
