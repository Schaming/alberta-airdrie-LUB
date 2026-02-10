import json
import os
import re
from docling.document_converter import DocumentConverter

# --- CONFIGURATION ---
INPUT_FOLDER = r"C:\Users\15877\alberta-airdrie-LUB\scripts\pdfs"
OUTPUT_FOLDER = r"C:\Users\15877\alberta-airdrie-LUB\scripts\JSON"

def inputfile_to_JSON():
    if not os.path.exists(OUTPUT_FOLDER):
        os.makedirs(OUTPUT_FOLDER)
    
    print("Initializing Docling OCR engine...")
    converter = DocumentConverter()
    pdf_files = [f for f in os.listdir(INPUT_FOLDER) if f.lower().endswith('.pdf')]
    
    for filename in pdf_files:
        input_path = os.path.join(INPUT_FOLDER, filename)
        output_path = os.path.join(OUTPUT_FOLDER, os.path.splitext(filename)[0] + ".json")
        print(f"--- Processing: {filename} ---")
        
        try:
            result = converter.convert(input_path)
            extracted_blocks = [item.text.strip() for item, _ in result.document.iterate_items() if hasattr(item, "text")]

            final_data = []
            current_term = None
            current_text_parts = []
            
            # Pattern 1: Standard "Term means" (Lethbridge, Ashcroft, Red Deer, Airdrie)
            means_pattern = re.compile(r"^(.+?)\s+means(?:\s+any\s+of\s+the\s+following)?\s*:?", re.IGNORECASE)
            
            # Pattern 2: Beaumont Table style - Looks for a quoted word on its own line
            table_term_pattern = re.compile(r"^\"([^\",]+)\"$") 

            for content in extracted_blocks:
                # 1. Skip junk/headers/footers
                if not content or any(x in content for x in ["Page |", "Page ", "PART 6", "PART 1"]): 
                    continue
                
                # 2. Skip "DELETED" entries (Lethbridge)
                if content.strip().upper() == "DELETED":
                    if current_term: save_entry(final_data, current_term, current_text_parts)
                    current_term = None
                    current_text_parts = []
                    continue

                # 3. Check for Standard "Means" Pattern
                match_means = means_pattern.search(content)
                
                # 4. Check for Beaumont Term Pattern (e.g. "Caliper")
                match_table = table_term_pattern.match(content)

                if match_means:
                    if current_term: save_entry(final_data, current_term, current_text_parts)
                    current_term = match_means.group(1).strip()
                    after = content[match_means.end():].strip()
                    current_text_parts = [after] if after else []

                elif match_table:
                    if current_term: save_entry(final_data, current_term, current_text_parts)
                    current_term = match_table.group(1).strip()
                    current_text_parts = []

                elif content in ['","', ',"', '",', '"']:
                    # Just a Beaumont table separator - ignore it
                    continue
                
                else:
                    if current_term:
                        # Clean Beaumont artifacts (,"...) and append text
                        clean_content = content.strip().lstrip(',"').rstrip('"').strip()
                        if clean_content:
                            current_text_parts.append(clean_content)

            # Final save for the last term in the file
            if current_term:
                save_entry(final_data, current_term, current_text_parts)

            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(final_data, f, indent=2)
            print(f"   Success! Extracted {len(final_data)} terms.")

        except Exception as e:
            print(f"   Error: {e}")

def save_entry(output_list, term, text_parts):
    full_text = " ".join(text_parts).strip()
    # Ensure "means" formatting remains consistent
    full_text = re.sub(r"^(?:means:?\s+)+", "", full_text, flags=re.IGNORECASE)
    
    # Validation: Ensure we have a real term and a real definition
    if term and full_text and len(term) < 100:
        output_list.append({
            "termID": term,
            "terms": term,
            "text": "means: " + full_text,
            "type": "General",
            "image": ""
        })

if __name__ == "__main__":
    inputfile_to_JSON()