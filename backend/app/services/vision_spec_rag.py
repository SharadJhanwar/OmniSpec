import base64
import os
import json
from typing import Dict, Any, Optional
from ..core.logging import logger

try:
    from langchain_openai import ChatOpenAI
    from langchain_core.messages import HumanMessage, SystemMessage
    HAS_OPENAI = bool(os.getenv("OPENAI_API_KEY"))
except ImportError:
    HAS_OPENAI = False


class VisionSpecSheetRAG:
    """
    Multimodal Vision Extraction Service (Vision RAG)
    Uses OpenAI GPT-4o-mini with Vision to extract mechanical dimensions, electrical ratings,
    approvals, and attribute key-value pairs from technical drawings and nameplate images.
    """

    @classmethod
    def extract_from_image_bytes(cls, image_bytes: bytes, mime_type: str = "image/jpeg") -> Dict[str, Any]:
        if not HAS_OPENAI:
            return {
                "success": False,
                "error": "OpenAI API key not configured for Vision RAG."
            }

        try:
            b64_image = base64.b64encode(image_bytes).decode("utf-8")
            data_url = f"data:{mime_type};base64,{b64_image}"

            llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

            prompt = (
                "You are an expert industrial spec sheet vision analyzer.\n"
                "Analyze this product spec sheet, technical drawing, or label image.\n"
                "Extract structured fields into valid JSON with this schema:\n"
                "{\n"
                '  "mfg_part_number": "<MPN>",\n'
                '  "manufacturer_name": "<Manufacturer>",\n'
                '  "brand_name": "<Brand with trademark if visible>",\n'
                '  "dimensions": {"length": "", "width": "", "height": "", "uom": "in"},\n'
                '  "electrical_specs": {"voltage": "", "amperage": "", "wattage": ""},\n'
                '  "attributes": {"key": "val"},\n'
                '  "standard_approvals": "UL Listed|Energy Star",\n'
                '  "description": "<Concise summary>"\n'
                "}\n"
                "Return ONLY valid raw JSON."
            )

            message = HumanMessage(
                content=[
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": data_url}}
                ]
            )

            res = llm.invoke([message])
            content = res.content.strip()
            if content.startswith("```json"):
                content = content.replace("```json", "").replace("```", "").strip()

            parsed = json.loads(content)
            return {
                "success": True,
                "extracted_data": parsed
            }
        except Exception as e:
            logger.error(f"[OmniSpec] Vision Spec RAG failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
