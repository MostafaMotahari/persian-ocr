import argparse
import logging
from persian_ocr import PDFUploader

LOGGER = logging.getLogger('persian_ocr')


def help_command():
    print("📘 General Help")
    print("Usage: python main.py [options]")
    print("Use --file or --dir to process PDFs. Add --headless to run without GUI.")
    print("\nAvailable categories:")
    print("  - PDF args:       pdf_arg_help()")
    print("  - Image args:     img_arg_help()")
    print("  - Browser args:   browser_arg_help()")
    print("Example:")
    print("  python main.py --file my.pdf --browser chrome --timeout 30\n")

def pdf_arg_help():
    print("📄 PDF Arguments Help")
    print("--file <path>         Path to a single PDF file to upload.")
    print("--dir <directory>     Path to a directory containing multiple PDFs.")
    print("You must specify either --file or --dir.")
    print("Example:")
    print("  python main.py --file ./input/resume.pdf\n")

def img_arg_help():
    print("🖼️ Image Arguments Help (for OCR or future use)")
    print("--img <path>          Path to a single image file (JPG/PNG).")
    print("--img-dir <directory> Directory of image files.")
    print("(Note: Not implemented yet)\n")

def browser_arg_help():
    print("🌐 Browser Arguments Help")
    print("--browser <name>      Choose browser: chrome, firefox, edge, safari")
    print("--headless            Run the browser in headless (no UI) mode.")
    print("--timeout <seconds>   Time to wait for elements, downloads, etc.")
    print("Example:")
    print("  python main.py --file sample.pdf --browser firefox --headless\n")

def parse_args():
    parser = argparse.ArgumentParser(
        description="Automate PDF upload and download using SeleniumBase.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )

    parser.add_argument(
        "--timeout", type=int, default=30,
        help="Maximum time (in seconds) to wait for elements or downloads."
    )

    parser.add_argument(
        "--browser", type=str, choices=["chrome", "firefox", "edge", "safari"], default="chrome",
        help="Browser to use for automation."
    )

    parser.add_argument(
        "--file", type=str,
        help="Path to a single PDF file to upload."
    )

    parser.add_argument(
        "--dir", type=str,
        help="Directory path containing multiple PDF files to process."
    )

    parser.add_argument(
        "--headless", action="store_true",
        help="Run the browser in headless mode."
    )

    args = parser.parse_args()

    # Validate file/dir input
    if not args.file and not args.dir:
        parser.error("You must specify either --file or --dir")

    return args

def main():
    args = parse_args()

    print(f"Selected Browser : {args.browser}")
    print(f"Headless Mode    : {'ON' if args.headless else 'OFF'}")
    print(f"Timeout          : {args.timeout} seconds")
    if args.file:
        print(f"File to upload   : {args.file}")
    if args.dir:
        print(f"Directory to scan: {args.dir}")

    uploader = PDFUploader(file=args.file, dir=args.dir, timeout=args.timeout, browser=args.browser, headless=args.headless)
    processed_files = uploader.upload_and_process()
    if processed_files:
        LOGGER.info(f"These files downloaded successfully: {', '.join(processed_files)}")
    else:
        LOGGER.warning("No file downloaded")


if __name__ == "__main__":
    main()
