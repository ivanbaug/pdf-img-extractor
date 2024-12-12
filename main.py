
# STEP 1 
# import libraries 
import fitz 
import io 

from PIL import Image 

# Image.MAX_IMAGE_PIXELS = 933120000 # In case of decompression error

# STEP 2 
# file path you want to extract images from 
filename = 'p3'
file = f"{filename}.PDF"
  
# open the file 
pdf_file = fitz.open(file) 
  
# STEP 3 
# iterate over PDF pages 
for page_index in range(len(pdf_file)): 
  
    # get the page itself 
    page = pdf_file[page_index] 
    image_list = page.get_images() 
  
    # printing number of images found in this page 
    if image_list: 
        print( 
            f"[+] Found a total of {len(image_list)} images in page {page_index}") 
    else: 
        print("[!] No images found on page", page_index) 
    for image_index, img in enumerate(page.get_images(), start=1): 
  
        # get the XREF of the image 
        xref = img[0] 
  
        # extract the image bytes 
        base_image = pdf_file.extract_image(xref) 
        image_bytes = base_image["image"] 
  
        # get the image extension 
        image_ext = base_image["ext"]
        # Save the image to disk
        image = Image.open(io.BytesIO(image_bytes))
        image.save(open(f"{filename}_image{page_index + 1}_{image_index}.{image_ext}", "wb"))
        print(f"[+] Extracted image {image_index} from page {page_index + 1}")


if __name__ == "__main__":
    print("Done!")