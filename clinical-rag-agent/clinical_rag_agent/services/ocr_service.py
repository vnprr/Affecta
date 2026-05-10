class OcrService:
    async def extract_text(self, file_bytes: bytes, filename: str = "") -> str:
        del filename
        return file_bytes.decode("utf-8", errors="ignore")

