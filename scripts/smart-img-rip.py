import os
import fitz  # PyMuPDF
import re

# --- CONFIGURATION ---
INPUT_FOLDER = r"C:\Users\15877\alberta-airdrie-LUB\scripts\pdfs"
IMAGE_OUTPUT_FOLDER = r"C:\Users\15877\alberta-airdrie-LUB\scripts\JSON\images"

def slugify(text):
    """Turns '**Deck**, Ground Level' into 'Deck_Ground_Level'"""
    # Remove markdown bolding and clean up
    text = text.replace('**', '').replace('__', '').strip()
    return re.sub(r'[^\w\s-]', '', text).strip().replace(' ', '_')

def smart_rip_images():
    if not os.path.exists(IMAGE_OUTPUT_FOLDER):
        os.makedirs(IMAGE_OUTPUT_FOLDER)
    
    pdf_files = [f for f in os.listdir(INPUT_FOLDER) if f.lower().endswith('.pdf')]
    
    for filename in pdf_files:
        doc = fitz.open(os.path.join(INPUT_FOLDER, filename))
        print(f"--- Smart Ripping (Rich Text Aware): {filename} ---")
        
        current_term = "General_Image"
        img_counts = {}

        for page_index in range(len(doc)):
            page = doc[page_index]
            text_instances = page.get_text("blocks") 
            image_info = page.get_images(full=True)
            
            for img_index, img_meta in enumerate(image_info):
                xref = img_meta[0]
                img_rects = page.get_image_rects(xref)
                if not img_rects: continue
                img_y = img_rects[0].y0 

                best_term = current_term
                for block in text_instances:
                    block_text = block[4].strip()
                    block_y = block[1]
                    
                    if block_y < img_y:
                        # UPDATED REGEX: Now looks for optional ** or __ markers around the term
                        # This matches: "Banner Sign means", "**Banner Sign** means", etc.
                        match = re.search(r"^(?:\*\*|__)?(.+?)(?:\*\*|__)?\s+means", block_text, re.IGNORECASE)
                        if match:
                            best_term = slugify(match.group(1))
                
                current_term = best_term
                base_image = doc.extract_image(xref)
                
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