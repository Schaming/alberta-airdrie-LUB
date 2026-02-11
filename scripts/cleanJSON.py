import json
import os
import re

# --- CONFIGURATION ---
RAW_JSON_FOLDER = r"C:\Users\15877\alberta-airdrie-LUB\scripts\JSON"
IMAGE_FOLDER = r"C:\Users\15877\alberta-airdrie-LUB\scripts\JSON\images"
FINAL_OUTPUT_FOLDER = r"C:\Users\15877\alberta-airdrie-LUB\scripts\JSON\final"

def slugify(text):
    clean = text.replace('**', '').replace('__', '').strip()
    return re.sub(r'[^\w\s-]', '', clean).strip().replace(' ', '_')

def reconstruct_and_link():
    if not os.path.exists(FINAL_OUTPUT_FOLDER): os.makedirs(FINAL_OUTPUT_FOLDER)
    
    available_images = os.listdir(IMAGE_FOLDER) if os.path.exists(IMAGE_FOLDER) else []
    raw_files = [f for f in os.listdir(RAW_JSON_FOLDER) if f.endswith('_RAW.json')]
    
    for filename in raw_files:
        with open(os.path.join(RAW_JSON_FOLDER, filename), 'r', encoding='utf-8') as f:
            raw_data = json.load(f)
        
        final_definitions = []
        i = 0
        while i < len(raw_data):
            item = raw_data[i]
            
            if item['type'] == 'text':
                content = item['content'].strip()
                
                # Look for the start of a definition: "Term means:"
                # Updated regex to handle the Rich Text (**) markers
                match = re.search(r"^(?:\*\*|__)?(.+?)(?:\*\*|__)?\s+means[:\s]*(.*)$", content, re.IGNORECASE | re.DOTALL)
                
                if match:
                    original_term = match.group(1).strip()
                    definition_text = match.group(2).strip()
                    term_id = slugify(original_term)
                    
                    # --- THE COLLECTOR LOOP ---
                    # Now we look ahead and grab EVERYTHING until the next definition starts
                    j = i + 1
                    while j < len(raw_data):
                        next_item = raw_data[j]
                        
                        # Stop if we hit an image (images are handled separately by ID) or a table
                        if next_item['type'] != 'text':
                            break
                            
                        next_content = next_item['content'].strip()
                        
                        # Stop if the next line is a NEW definition (contains "means")
                        if re.search(r"\s+means[:\s]", next_content, re.IGNORECASE):
                            break
                            
                        # Otherwise, it's a list item (a, b, c) or a continuation. Append it!
                        # We use \n for a clean RTF/Markdown line break
                        definition_text += "\n" + next_content
                        j += 1
                    
                    # Update our main loop index to where the collector stopped
                    i = j - 1 

                    # Precise Image Linking
                    found_images = [img for img in available_images if img.split('_img')[0] == term_id]
                    image_string = ";".join(found_images)
                    
                    final_definitions.append({
                        "termID": term_id,
                        "terms": original_term.replace('**', ''),
                        "text": definition_text.strip(), 
                        "type": "General",
                        "image": image_string
                    })
            i += 1
        
        output_name = filename.replace('_RAW.json', '_FINAL.json')
        with open(os.path.join(FINAL_OUTPUT_FOLDER, output_name), 'w', encoding='utf-8') as f:
            json.dump(final_definitions, f, indent=2)
            
    print(f"Success! Lists are now preserved in {FINAL_OUTPUT_FOLDER}")

if __name__ == "__main__":
    reconstruct_and_link()