import easyocr
from PIL import Image
import io

class ImageToTextAgent:
    def __init__(self, lang_list=None):
        self.reader = easyocr.Reader(lang_list or ['en'], gpu=False)

    def extract_ingredients(self, image_bytes) -> str:
        try:
            result = self.reader.readtext(image_bytes, detail=0, paragraph=True)
            lines = [line.strip() for line in result if line.strip()]
            return ", ".join(lines)
        except Exception as e:
            return f"❌ OCR failed: {e}"