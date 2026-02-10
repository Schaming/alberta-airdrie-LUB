import os
import fitz  # PyMuPDF
import re

# --- CONFIGURATION ---
INPUT_FOLDER = r"C:\Users\15877\alberta-airdrie-LUB\scripts\pdfs"
IMAGE_OUTPUT_FOLDER = r"C:\Users\15877\alberta-airdrie-LUB\scripts\JSON\images"

def slugify(text):
    """Turns 'Deck, Ground Level' into 'Deck_Ground_Level'"""
    text = text.replace('**', '').strip()
    return re.sub(r'[^\w\s-]', '', text).strip().replace(' ', '_')

def smart_rip_images():
    if not os.path.exists(IMAGE_OUTPUT_FOLDER):
        os.makedirs(IMAGE_OUTPUT_FOLDER)
    
    pdf_files = [f for f in os.listdir(INPUT_FOLDER) if f.lower().endswith('.pdf')]
    
    for filename in pdf_files:
        doc = fitz.open(os.path.join(INPUT_FOLDER, filename))
        print(f"--- Smart Ripping: {filename} ---")
        
        current_term = "General_Image"
        img_counts = {}

        for page_index in range(len(doc)):
            page = doc[page_index]
            
            # 1. SCAN THE PAGE TEXT TO FIND THE "LAST DEFINITION"
            # We look for terms that likely start a definition
            text_instances = page.get_text("blocks") 
            # Blocks are (x0, y0, x1, y1, "text", block_no, block_type)
            
            # 2. FIND EMBEDDED IMAGES
            image_info = page.get_images(full=True)
            
            for img_index, img_meta in enumerate(image_info):
                xref = img_meta[0]
                
                # Get image location on page to find text above it
                img_rects = page.get_image_rects(xref)
                if not img_rects: continue
                img_y = img_rects[0].y0 # The vertical position of the image

                # Look for the closest text block ABOVE this image
                best_term = current_term
                for block in text_instances:
                    block_text = block[4].strip()
                    block_y = block[1]
                    
                    # If this block is above the image and looks like a Term (has "means")
                    if block_y < img_y:
                        match = re.search(r"^(.+?)\s+means", block_text, re.IGNORECASE)
                        if match:
                            best_term = slugify(match.group(1))
                
                current_term = best_term
                
                # 3. EXTRACT AND SAVE WITH SMART NAME
                base_image = doc.extract_image(xref)
                
                # Increment counter for this term (e.g., Deck_img1, Deck_img2)
                count = img_counts.get(current_term, 0) + 1
                img_counts[current_term] = count
                
                final_name = f"{current_term}_img{count}.{base_image['ext']}"
                save_path = os.path.join(IMAGE_OUTPUT_FOLDER, final_name)
                
                with open(save_path, "wb") as f:
                    f.write(base_image["image"])
                
                print(f"   Saved: {final_name}")

        doc.close()

if __name__ == "__main__":
    smart_rip_images()