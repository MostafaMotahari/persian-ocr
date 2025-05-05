import logging
from persian_ocr.pdf.classes import PDFLoader, PDFUploader

logger = logging.getLogger("persian_ocr")
console_logger = logging.StreamHandler()
file_logger = logging.FileHandler("log.log", mode="a", encoding="utf-8")
logger.addHandler(console_logger)
logger.addHandler(file_logger)
formatter = logging.Formatter("[{asctime}] - {levelname} - {message}", style="{", datefmt="%Y-%m-%d %H:%M")
console_logger.setFormatter(formatter)
file_logger.setFormatter(formatter)
logger.setLevel(logging.INFO)
