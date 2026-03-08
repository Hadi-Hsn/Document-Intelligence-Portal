"""
Document Intelligence Portal
A Streamlit application for uploading, extracting, and analyzing documents
using OpenAI for contract intelligence.
"""

import os
import streamlit as st
from dotenv import load_dotenv

from extractors import extract_text
from analyzer import analyze_document

# Load environment variables
load_dotenv()

# ── Page Config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Document Intelligence Portal",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ───────────────────────────────────────────────────────────────
st.markdown(
    """
<style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 700;
        color: #1a1a2e;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.1rem;
        color: #6c757d;
        margin-bottom: 2rem;
    }
    .severity-high {
        background-color: #f8d7da;
        border-left: 4px solid #dc3545;
        padding: 12px 16px;
        border-radius: 4px;
        margin-bottom: 12px;
    }
    .severity-medium {
        background-color: #fff3cd;
        border-left: 4px solid #ffc107;
        padding: 12px 16px;
        border-radius: 4px;
        margin-bottom: 12px;
    }
    .severity-low {
        background-color: #d1ecf1;
        border-left: 4px solid #17a2b8;
        padding: 12px 16px;
        border-radius: 4px;
        margin-bottom: 12px;
    }
    .metadata-card {
        background-color: #f8f9fa;
        border: 1px solid #dee2e6;
        border-radius: 8px;
        padding: 16px;
        margin-bottom: 8px;
    }
    .quote-block {
        border-left: 3px solid #6c757d;
        padding-left: 12px;
        font-style: italic;
        color: #495057;
        margin: 8px 0;
    }
</style>
""",
    unsafe_allow_html=True,
)

# ── Header ───────────────────────────────────────────────────────────────────
st.markdown(
    '<div class="main-header">📄 Document Intelligence Portal</div>',
    unsafe_allow_html=True,
)
st.markdown(
    '<div class="sub-header">Upload contracts and documents for AI-powered analysis, metadata extraction, and risk detection.</div>',
    unsafe_allow_html=True,
)

# ── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.header("⚙️ Settings")

    # API Key input (optional override)
    api_key_input = st.text_input(
        "OpenAI API Key",
        type="password",
        placeholder="sk-...",
        help="Enter your OpenAI API key. This overrides the .env file setting.",
    )
    if api_key_input:
        os.environ["OPENAI_API_KEY"] = api_key_input

    st.divider()
    st.markdown("**Supported file types:**")
    st.markdown("- PDF (.pdf)")
    st.markdown("- Word (.doc, .docx)")
    st.markdown("- Images (.png, .jpg, .jpeg, .tiff)")

    st.divider()
    st.markdown("**How it works:**")
    st.markdown("1. Upload one or more files")
    st.markdown("2. Text is extracted automatically")
    st.markdown("3. OpenAI analyzes the content")
    st.markdown("4. View summary, metadata, and risks")

# ── File Upload ──────────────────────────────────────────────────────────────
uploaded_files = st.file_uploader(
    "Upload documents",
    type=["pdf", "doc", "docx", "png", "jpg", "jpeg", "tiff", "tif", "bmp", "webp"],
    accept_multiple_files=True,
    help="Upload one or more documents for analysis.",
)

if not uploaded_files:
    st.info("👆 Upload one or more documents to get started.")
    st.stop()

# ── Process Each File ────────────────────────────────────────────────────────
for uploaded_file in uploaded_files:
    st.divider()
    st.subheader(f"📁 {uploaded_file.name}")

    file_bytes = uploaded_file.read()
    file_size_kb = len(file_bytes) / 1024

    col1, col2 = st.columns(2)
    col1.metric("File Size", f"{file_size_kb:.1f} KB")
    col2.metric("File Type", uploaded_file.name.split(".")[-1].upper())

    # ── Step 1: Text Extraction ──────────────────────────────────────────
    with st.status("Extracting text...", expanded=False) as status:
        try:
            extracted_text = extract_text(file_bytes, uploaded_file.name)
            if not extracted_text.strip():
                st.warning("No text could be extracted from this file.")
                status.update(
                    label="Extraction complete (no text found)", state="complete"
                )
                continue
            status.update(
                label=f"Extracted {len(extracted_text):,} characters", state="complete"
            )
        except ValueError as e:
            st.error(f"❌ {str(e)}")
            status.update(label="Extraction failed", state="error")
            continue
        except Exception as e:
            st.error(f"❌ Error extracting text: {str(e)}")
            status.update(label="Extraction failed", state="error")
            continue

    # ── Step 2: AI Analysis ──────────────────────────────────────────────
    with st.status("Analyzing with OpenAI...", expanded=False) as status:
        try:
            analysis = analyze_document(extracted_text, uploaded_file.name)
            status.update(label="Analysis complete ✓", state="complete")
        except ValueError as e:
            st.error(f"❌ {str(e)}")
            status.update(label="Analysis failed", state="error")
            continue
        except Exception as e:
            st.error(f"❌ Error during analysis: {str(e)}")
            status.update(label="Analysis failed", state="error")
            continue

    # ── Display Results ──────────────────────────────────────────────────
    tab1, tab2, tab3, tab4, tab5 = st.tabs(
        [
            "📝 Summary",
            "🏷️ Metadata",
            "⚠️ Risks & Alerts",
            "📌 Key Clauses",
            "📄 Full Text",
        ]
    )

    # ── Tab 1: Summary ───────────────────────────────────────────────────
    with tab1:
        summary = analysis.get("summary", "No summary available.")
        st.markdown(summary)

        if "_note" in analysis:
            st.info(f"ℹ️ {analysis['_note']}")

    # ── Tab 2: Metadata ──────────────────────────────────────────────────
    with tab2:
        metadata = analysis.get("metadata", {})
        if not metadata:
            st.info("No metadata could be extracted.")
        else:
            # Main metadata fields
            simple_fields = [
                ("document_type", "Document Type"),
                ("contract_type", "Contract Type"),
                ("effective_date", "Effective Date"),
                ("expiration_date", "Expiration / Renewal Date"),
                ("jurisdiction", "Jurisdiction / Governing Law"),
                ("payment_terms", "Payment Terms"),
            ]

            cols = st.columns(2)
            for i, (key, label) in enumerate(simple_fields):
                value = metadata.get(key)
                if value:
                    with cols[i % 2]:
                        st.markdown(
                            f'<div class="metadata-card"><strong>{label}</strong><br>{value}</div>',
                            unsafe_allow_html=True,
                        )

            # Parties
            parties = metadata.get("parties", [])
            if parties:
                st.markdown("**Parties Involved:**")
                for party in parties:
                    if isinstance(party, dict):
                        name = party.get("name", party.get("party", str(party)))
                        role = party.get("role", "")
                        st.markdown(f"- **{name}** {f'({role})' if role else ''}")
                    else:
                        st.markdown(f"- {party}")

            # Person names
            persons = metadata.get("person_names", [])
            if persons:
                st.markdown("**Person Names:**")
                st.markdown(", ".join(str(p) for p in persons))

            # Company names
            companies = metadata.get("company_names", [])
            if companies:
                st.markdown("**Company Names:**")
                st.markdown(", ".join(str(c) for c in companies))

            # Clause summaries
            clause_fields = [
                ("termination_terms", "Termination Terms"),
                ("force_majeure", "Force Majeure"),
                ("liability_indemnity", "Liability / Indemnity"),
                ("confidentiality", "Confidentiality Obligations"),
            ]
            for key, label in clause_fields:
                value = metadata.get(key)
                if value:
                    with st.expander(f"📋 {label}"):
                        st.markdown(value)

            # Other metadata
            other = metadata.get("other_metadata")
            if other and isinstance(other, dict):
                with st.expander("📋 Other Metadata"):
                    for k, v in other.items():
                        st.markdown(f"- **{k}:** {v}")

    # ── Tab 3: Risks & Alerts ────────────────────────────────────────────
    with tab3:
        risks = analysis.get("risks", [])
        if not risks:
            st.success("✅ No significant risks or alerts detected.")
        else:
            # Summary counts
            high = sum(1 for r in risks if r.get("severity", "").lower() == "high")
            medium = sum(1 for r in risks if r.get("severity", "").lower() == "medium")
            low = sum(1 for r in risks if r.get("severity", "").lower() == "low")

            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Total Alerts", len(risks))
            c2.metric("🔴 High", high)
            c3.metric("🟡 Medium", medium)
            c4.metric("🔵 Low", low)

            st.markdown("---")

            # Sort risks: High first, then Medium, then Low
            severity_order = {"high": 0, "medium": 1, "low": 2}
            sorted_risks = sorted(
                risks,
                key=lambda r: severity_order.get(r.get("severity", "").lower(), 3),
            )

            for risk in sorted_risks:
                severity = risk.get("severity", "Medium").lower()
                css_class = f"severity-{severity}"
                title = risk.get("title", "Unnamed Risk")
                category = risk.get("category", "")
                explanation = risk.get("explanation", "")
                quoted = risk.get("quoted_text", "")

                severity_icon = {"high": "🔴", "medium": "🟡", "low": "🔵"}.get(
                    severity, "⚪"
                )

                st.markdown(
                    f'<div class="{css_class}">'
                    f"<strong>{severity_icon} {title}</strong>"
                    f'{f" &nbsp;|&nbsp; <em>{category}</em>" if category else ""}'
                    f" &nbsp;|&nbsp; Severity: <strong>{severity.capitalize()}</strong>"
                    f"</div>",
                    unsafe_allow_html=True,
                )

                if quoted:
                    st.markdown(
                        f'<div class="quote-block">"{quoted}"</div>',
                        unsafe_allow_html=True,
                    )

                if explanation:
                    st.markdown(explanation)

                st.markdown("")

    # ── Tab 4: Key Clauses ───────────────────────────────────────────────
    with tab4:
        clauses = analysis.get("important_clauses", [])
        if not clauses:
            st.info("No key clauses highlighted.")
        else:
            for clause in clauses:
                title = clause.get("title", "Unnamed Clause")
                quoted = clause.get("quoted_text", "")
                significance = clause.get("significance", "")

                with st.expander(f"📌 {title}"):
                    if quoted:
                        st.markdown(
                            f'<div class="quote-block">"{quoted}"</div>',
                            unsafe_allow_html=True,
                        )
                    if significance:
                        st.markdown(f"**Significance:** {significance}")

    # ── Tab 5: Full Text ─────────────────────────────────────────────────
    with tab5:
        st.text_area(
            "Extracted Text",
            value=extracted_text,
            height=500,
            disabled=True,
            label_visibility="collapsed",
        )
        st.download_button(
            "⬇️ Download Extracted Text",
            data=extracted_text,
            file_name=f"{uploaded_file.name}_extracted.txt",
            mime="text/plain",
        )
