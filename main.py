import fitz 
import io
from PIL import Image

import argparse
from pathlib import Path

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
        img_leading_zeroes = len(str(len(image_list)))
        for image_index, img in enumerate(page.get_images(), start=1):
            xref = img[0]
            base_image = pdf.extract_image(xref)
            image_bytes = base_image["image"]
            image_ext = base_image["ext"]
            try:
                image = Image.open(io.BytesIO(image_bytes))
            except Image.DecompressionBombError as e:
                print(f"[!] Error opening image {image_index} from page {page_num + 1}: {e}")
                print(f"[!] Consider using the --allow-large-images flag to remove the limit on the maximum image size that can be opened")
                continue

            output_file = output_dir / f"{pdf_file.stem}_page{str(page_num + 1).zfill(page_leading_zeroes)}_img{str(image_index).zfill(img_leading_zeroes)}.{image_ext}"
            image.save(open(output_file, "wb"))

def get_output_dir(output_dir_str: str) -> Path:
    if output_dir_str == None or output_dir_str == "":
        output_dir_str = str(Path.cwd() / "output")
    elif Path(output_dir_str) == Path.cwd():
        output_dir_str = str(Path.cwd() / "output")    

    output_dir = Path(output_dir_str)
    if output_dir.exists() and not output_dir.is_dir():
        raise NotADirectoryError(f"Path exists but is not a directory: {output_dir}")

    try:
        if not output_dir.exists():
            output_dir.mkdir(parents=True)
    except OSError as e:
        print(f"[!] Error creating output directory: {e}")
        print(f"[!] Defaulting to current directory.")
        output_dir = Path.cwd() / "output"
        if not output_dir.exists():
            output_dir.mkdir(parents=True)

    return output_dir

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("file_path", nargs='?', default=None, help="Path to the PDF file")
    parser.add_argument("-d", "--dir", nargs='?', default=None, help="Directory of pdf files to extract images from")
    parser.add_argument("-o", "--output-dir", nargs='?', default=None, help="Output directory to save images, defaluts to current_directory/output")
    parser.add_argument("--allow-large-images", action='store_true', help="Removes the limit on the maximum image size that can be opened")

    args = parser.parse_args()
    print(args)

    file_path_str = args.file_path
    dir_path_str = args.dir
    output_dir_str = args.output_dir
    allow_large_images = args.allow_large_images

    if allow_large_images:
        Image.MAX_IMAGE_PIXELS = 933120000 # Allows for very large images to be opened

    if file_path_str != None and dir_path_str != None:
        print("Please provide either a file path or a directory path, not both.")
        exit(2)

    if file_path_str == None and dir_path_str == None:
        print("No path provided, defaulting to current directory.")
        dir_path_str = str(Path.cwd())

    # Validate output directory
    try:
        output_dir = get_output_dir(output_dir_str)
    except NotADirectoryError as e:
        print(f"Error: {e}")
        exit(1)

    # Case 1: Extract images from a single PDF file

    if file_path_str != None:
        file_path = Path(file_path_str)
        if not file_path.exists():
            print(f"File not found: {file_path}")
            exit(1)
        elif not file_path.is_file() or not file_path.suffix.lower() == ".pdf":
            print(f"Invalid file: {file_path}, Must have .pdf extension")
            exit(1)

        extract_images_from_pdf(file_path, output_dir)
        print("Finished extracting images")
        print(f"[+] Images extracted from {file_path}")
        print(f"[+] Images saved to {output_dir}")
        exit(0)

    # Case 2: Extract images from all PDF files in a directory

    if dir_path_str != None:
        dir_path = Path(dir_path_str)
        if not dir_path.exists():
            print(f"Directory not found: {dir_path}")
            exit(1)
        elif not dir_path.is_dir():
            print(f"Invalid directory: {dir_path}")
            exit(1)

        pdf_files = [file for file in dir_path.iterdir() if file.is_file() and file.suffix.lower() == ".pdf"]
        print(f"Found {len(pdf_files)} PDF files in {dir_path}")

        for file in pdf_files:
            extract_images_from_pdf(file, output_dir)
            print(f"[+] Images extracted from {file}")
        print("Finished extracting images")
        print(f"[+] Images saved to {output_dir}")
        exit(0)
