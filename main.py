import fitz 
import io
from PIL import Image

import argparse
from pathlib import Path

Image.MAX_IMAGE_PIXELS = 933120000 # In case of decompression error



def extract_images_from_pdf(pdf_file: Path, output_dir: Path) -> None:
    # validate file path
    if not pdf_file.exists() or not pdf_file.is_file():
        raise FileNotFoundError(f"File not found: {pdf_file}")
    if not pdf_file.suffix.lower() == ".pdf":
        raise ValueError(f"File {pdf_file} is not a PDF file.")

    # open the file
    pdf = fitz.open(pdf_file)
    print(f"[+] Extracting images from {pdf_file}")

    page_leading_zeroes = len(str(len(pdf)))

    for page_num in range(len(pdf)):
        page = pdf[page_num]
        image_list = page.get_images()
        if image_list:
            print(f"[+] Found a total of {len(image_list)} images in page {page_num}")
        else:
            print(f"[!] No images found on page {page_num}")
        img_leading_zeroes = len(str(len(image_list)))
        for image_index, img in enumerate(page.get_images(), start=1):
            xref = img[0]
            base_image = pdf.extract_image(xref)
            image_bytes = base_image["image"]
            image_ext = base_image["ext"]
            image = Image.open(io.BytesIO(image_bytes))
            output_dir = get_output_dir(output_dir)
            output_file = output_dir / f"{pdf_file.stem}_page{str(page_num + 1).zfill(page_leading_zeroes)}_img{str(image_index).zfill(img_leading_zeroes)}.{image_ext}"
            image.save(open(output_file, "wb"))
            print(f"[+] Extracted image {image_index} from page {page_num + 1}")

def get_output_dir(output_dir: Path) -> Path:
    if output_dir == None or output_dir == Path.cwd():
        output_dir = Path.cwd() / "output"
        
    if not output_dir.exists():
        output_dir.mkdir(parents=True)

    return output_dir

if __name__ == "__main__":
    current_dir = Path.cwd()
    print(current_dir)
    # get list of files in current directory
    pdf_files = [file for file in current_dir.iterdir() if file.is_file() and file.suffix.lower() == ".pdf"]
    print(f"Found {len(pdf_files)} PDF files in current directory")

    for file in pdf_files:
        extract_images_from_pdf(file, current_dir)