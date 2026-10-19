# backend/app/tools/pdf_parser.py
import fitz  # PyMuPDF
import base64
import os
from typing import Tuple, List
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage
from app.config import settings


def extract_text_from_pdf(pdf_path: str, doc_label: str = "Document") -> Tuple[str, List[str]]:
    """
    Extracts text from a PDF file.
    If the PDF is a scanned image (<50 chars extracted), automatically falls back to Gemini Vision OCR.
    Returns: (extracted_text, telemetry_logs)
    """
    logs: List[str] = []
    if not os.path.exists(pdf_path):
        logs.append(f"[ERROR] {doc_label} file not found at: {pdf_path}")
        return "", logs

    try:
        doc = fitz.open(pdf_path)
        extracted_pages = []
        
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            page_text = page.get_text("text").strip()
            if page_text:
                extracted_pages.append(f"--- Page {page_num + 1} ---\n{page_text}")

        full_text = "\n\n".join(extracted_pages).strip()

        # Check if enough text was extracted (standard digital PDF)
        if len(full_text) >= 50:
            logs.append(
                f"[SUCCESS] Extracted {len(full_text)} characters from {doc_label} ({len(doc)} pages) via PyMuPDF."
            )
            doc.close()
            return full_text, logs

        # SELF-HEALING FALLBACK: Scanned PDF detected (<50 chars) -> Switch to Gemini Vision OCR
        logs.append(
            f"[WARN] {doc_label} yielded <50 chars via standard text layer (likely a scanned PDF). "
            f"Triggering Gemini Vision OCR fallback..."
        )
        
        vision_llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            google_api_key=settings.GEMINI_API_KEY,
            temperature=0.0
        )

        ocr_pages = []
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            # Render page to high-res PNG image (150 DPI is ideal for OCR speed + accuracy)
            pix = page.get_pixmap(dpi=150)
            img_bytes = pix.tobytes("png")
            img_b64 = base64.b64encode(img_bytes).decode("utf-8")

            message = HumanMessage(
                content=[
                    {
                        "type": "text",
                        "text": (
                            f"Perform accurate OCR on page {page_num + 1} of this {doc_label}. "
                            "Extract all text, tables, course names, grades, CGPA, skills, and links verbatim. "
                            "Preserve tabular structure using Markdown."
                        ),
                    },
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/png;base64,{img_b64}"},
                    },
                ]
            )
            response = vision_llm.invoke([message])
            ocr_pages.append(f"--- Page {page_num + 1} (Vision OCR) ---\n{response.content}")

        doc.close()
        ocr_full_text = "\n\n".join(ocr_pages).strip()
        logs.append(
            f"[RECOVERY] Successfully extracted {len(ocr_full_text)} characters from scanned {doc_label} via Gemini Vision."
        )
        return ocr_full_text, logs

    except Exception as e:
        logs.append(f"[ERROR] Failed to parse {doc_label}: {str(e)}")
        return "", logs