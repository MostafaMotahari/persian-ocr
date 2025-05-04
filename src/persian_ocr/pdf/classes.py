import os
import logging
from seleniumbase import BaseCase
from selenium.common.exceptions import TimeoutException

LOGGER = logging.getLogger('persian_ocr')


class PDFLoader:
    def __init__(self, file: str = None, dir: str = None):
        self.file = file
        self.dir = dir

    def check_dir_content(self):
        if not self.dir:
            LOGGER.warning("No directory specified.")
            return []

        if not os.path.isdir(self.dir):
            LOGGER.error(f"Directory does not exist: {self.dir}")
            return []

        pdf_files = [f for f in os.listdir(self.dir) if f.lower().endswith('.pdf')]
        LOGGER.info(f"Found {len(pdf_files)} PDF files in directory: {self.dir}")
        return pdf_files

    def check_file_existence(self):
        if not self.file:
            LOGGER.warning("No file specified.")
            return False

        if not os.path.isfile(self.file):
            LOGGER.error(f"File does not exist: {self.file}")
            return False

        if not self.file.lower().endswith('.pdf'):
            LOGGER.error(f"File is not a PDF: {self.file}")
            return False

        LOGGER.info(f"PDF file exists: {self.file}")
        return True

    def check_source(self):
        if self.file and self.dir:
            LOGGER.warning("Both file and directory are set. Choose one source.")
            return False

        if not self.file and not self.dir:
            LOGGER.error("No source provided. Specify either a file or a directory.")
            return False

        if self.file:
            return self.check_file_existence()

        if self.dir:
            content = self.check_dir_content()
            return bool(content)

        return False


class PDFUploader(BaseCase):
    def __init__(self, file: str = None, dir: str = None, browser: str = "firefox", headless: bool = True, timeout: int = 60):
        super().__init__()
        self.site_url = "https://www.i2pdf.com/pdf-to-text"
        self.timeout = timeout
        self.loader = PDFLoader(file=file, dir=dir)
        self.set_downloads_path("results/")
        self.browser = browser
        self.headless = headless

    def upload_and_process(self):
        if not self.loader.check_source():
            LOGGER.error("Invalid file or directory. Upload aborted.")
            return

        files = [self.loader.file] if self.loader.file else [
            os.path.join(self.loader.dir, f)
            for f in self.loader.check_dir_content()
        ]

        downloaded_files = []

        for file_path in files:
            self.open(self.site_url)
            self.choose_file("input[type=\"hidden\"]#sesrvice", file_path)
            LOGGER.info(f"Uploading file: {file_path}")

            try:
                self.wait_for_text(
                    "Loading Files, Please Wait ...",
                    selector="div.font-size-1.mb-3",
                    timeout=self.timeout
                )
                LOGGER.info(f"File uploaded successfully: {file_path}")

                start_btn_selector = "span.pr-2.pl-2"
                self.wait_for_element(start_btn_selector, timeout=self.timeout)
                LOGGER.info(f"File processed: {file_path}")

                self.click_active_element(start_btn_selector)
                LOGGER.info("Awaiting completion of processing...")

                a_selector = "a.btn.btn-primary.btn-lg.font-size-2.px-8.shadow-soft.text-center.text-left"
                self.wait_for_element_clickable(a_selector, timeout=15)
                self.click(a_selector)

                self.assert_downloaded_file("pdf2text.zip")
                downloaded_file_path = self.rename_download_to_original(file_path)
                downloaded_files.append(downloaded_file_path)

            except TimeoutException:
                LOGGER.error(f"Some processes can't be done within {self.timeout} seconds.")
                continue

        return downloaded_files

    def rename_download_to_original(self, original_file_path: str):
        original_filename = os.path.basename(original_file_path)
        original_prefix = os.path.splitext(original_filename)[0]

        downloaded_path = self.get_latest_download_file(timeout=self.timeout)
        downloaded_filename = os.path.basename(downloaded_path)
        downloaded_postfix = os.path.splitext(downloaded_filename)[1]

        renamed_path = os.path.join(self.get_downloads_path(), f"{original_prefix}{downloaded_postfix}")
        os.rename(downloaded_path, renamed_path)
        return renamed_path
