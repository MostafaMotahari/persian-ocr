import os
import logging
from seleniumbase import SB
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


class PDFUploader:
    def __init__(self, file: str = None, dir: str = None, browser: str = "firefox", headless: bool = True, timeout: int = 60):
        super().__init__()
        self.sb = SB(uc_cdp=True, browser=browser, headless=headless)
        self.site_url = "https://www.i2pdf.com/pdf-to-text"
        self.loader = PDFLoader(file=file, dir=dir)
        self.timeout = timeout

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
            with self.sb as sb:
                sb.open(self.site_url)
                sb.wait_for_ready_state_complete()

                file_selector = "input.dz-hidden-input"

                sb.assert_element_not_visible(file_selector)

                # Make file input visible manually unless selenium can't upload file into that tag.
                sb.execute_script("""
                  const el = document.querySelector('input.dz-hidden-input');
                  if (el) {
                    el.style.height = '100px';
                    el.style.visibility = 'visible';
                    el.style.width = '300px';
                    el.style.position = 'fixed';
                    el.style.top = '100px';
                    el.style.left = '100px';
                    el.style.opacity = 1;
                    el.style.zIndex = 9999;
                  }
                """)
                sb.wait_for_element_visible("input.dz-hidden-input", timeout=self.timeout)
                sb.choose_file(file_selector, file_path)

                LOGGER.info(f"Uploading file: {file_path}")

                try:
                    sb.wait_for_text(
                        "Loading Files, Please Wait ...",
                        selector="div.font-size-1.mb-3",
                        timeout=self.timeout
                    )
                    LOGGER.info(f"File uploaded successfully: {file_path}")

                    start_btn_selector = "button.pdf_to_text"
                    sb.wait_for_element_clickable(start_btn_selector, timeout=self.timeout)
                    sb.highlight(start_btn_selector)
                    LOGGER.info(f"File processed: {file_path}")

                    sb.click(start_btn_selector)
                    LOGGER.info("Awaiting completion of processing...")

                    a_selector = "a.btn.btn-primary.btn-lg.font-size-2.px-8.shadow-soft.text-center.text-left"
                    sb.wait_for_element_clickable(a_selector, timeout=self.timeout * 3)
                    sb.click(a_selector)

                    sb.assert_downloaded_file("pdf2text.zip")
                    file_name = os.path.basename(file_path)
                    downloaded_files.append(file_name)

                except TimeoutException:
                    LOGGER.error(f"Some processes can't be done within {self.timeout} seconds.")
                    continue

        return downloaded_files
