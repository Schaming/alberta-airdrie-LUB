import json
import os
import re

# --- CONFIGURATION ---
RAW_JSON_FOLDER = r"C:\Users\15877\alberta-airdrie-LUB\scripts\JSON"
IMAGE_FOLDER = r"C:\Users\15877\alberta-airdrie-LUB\scripts\JSON\images"
FINAL_OUTPUT_FOLDER = r"C:\Users\15877\alberta-airdrie-LUB\scripts\JSON\final"

def slugify(text):
    # Remove bolding and special chars, keep underscores
    text = text.replace('**', '').strip()
    return re.sub(r'[^\w\s-]', '', text).strip().replace(' ', '_')

def reconstruct_and_link():
    if not os.path.exists(FINAL_OUTPUT_FOLDER): os.makedirs(FINAL_OUTPUT_FOLDER)
    
    # Get all smart-named images
    available_images = os.listdir(IMAGE_FOLDER) if os.path.exists(IMAGE_FOLDER) else []
    
    raw_files = [f for f in os.listdir(RAW_JSON_FOLDER) if f.endswith('_RAW.json')]
    
    for filename in raw_files:
        with open(os.path.join(RAW_JSON_FOLDER, filename), 'r', encoding='utf-8') as f:
            raw_data = json.load(f)
        
        final_definitions = []
        
        for item in raw_data:
            if item['type'] == 'text':
                content = item['content']
                # Splitting "Term means Definition"
                match = re.search(r"^(.+?)\s+means\s+(.+)$", content, re.IGNORECASE | re.DOTALL)
                
                if match:
                    original_term = match.group(1).replace('**', '').strip()
                    definition_text = match.group(2).strip()
                    term_id = slugify(original_term)
                    
                    # --- MULTI-IMAGE SEARCH ---
                    # Find ALL images starting with this termID (e.g. Deck_img1, Deck_img2)
                    found_images = []
                    for img_file in available_images:
                        if img_file.startswith(term_id):
                            found_images.append(img_file)
                    
                    # Join images with ;
                    image_string = ";".join(found_images)
                    
                    # If we had multiple synonymous terms, we'd join them here with ; too
                    # For now, we ensure the primary term is clean
                    final_definitions.append({
                        "termID": term_id,
                        "terms": original_term, # If you add synonyms later, use ";" here
                        "text": definition_text,
                        "type": "General",
                        "image": image_string
                    })
        
        output_name = filename.replace('_RAW.json', '_FINAL.json')
        with open(os.path.join(FINAL_OUTPUT_FOLDER, output_name), 'w', encoding='utf-8') as f:
            json.dump(final_definitions, f, indent=2)
            
    print(f"Success! Delimited files created in: {FINAL_OUTPUT_FOLDER}")

if __name__ == "__main__":
    reconstruct_and_link()