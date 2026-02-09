import json
import os
import re

def convert_airdrie_to_standard(input_path, output_path):
    if not os.path.exists(input_path):
        print(f"Error: Could not find file at {input_path}")
        return

    with open(input_path, 'r', encoding='utf-8') as f:
        source_data = json.load(f)

    texts = source_data.get('texts', [])
    converted_definitions = []
    
    current_term = None
    current_text_parts = []

    # Regex to find "Term means:" or "Term means any of the following:"
    # It looks for the word 'means' preceded by a name and potentially a semicolon
    means_pattern = re.compile(r"(.+?)\s+means(?:\s+any\s+of\s+the\s+following)?\s*:")

    for item in texts:
        content = item.get('text', '').strip()
        if not content:
            continue

        # Check if the current block contains a definition trigger
        # We handle the case where a block might contain the end of one def AND the start of another
        match = means_pattern.search(content)
        
        if match:
            # 1. Extract the text before the 'means:' (this is the term candidate)
            term_candidate = match.group(1).strip()
            
            # 2. If there is a semicolon or period, the part before it belongs to the PREVIOUS definition
            # This is specifically what fixes the 'Banner Sign' issue.
            if ";" in term_candidate or ". " in term_candidate:
                # Find the last separator
                split_point = max(term_candidate.rfind(";"), term_candidate.rfind("."))
                preceding_text = term_candidate[:split_point + 1].strip()
                new_term = term_candidate[split_point + 1:].strip()
                
                # Add the preceding text to the current open definition
                if current_term and preceding_text:
                    current_text_parts.append(preceding_text)
            else:
                new_term = term_candidate

            # 3. Save the completed previous definition before starting the new one
            if current_term and current_text_parts:
                save_definition(converted_definitions, current_term, current_text_parts)

            # 4. Start the new definition with the text found after 'means:'
            current_term = new_term
            remaining_content = content[match.end():].strip()
            current_text_parts = [remaining_content] if remaining_content else []
            
        else:
            # If no 'means:' is found, just append the content to the current term
            if current_term:
                # Clean out Bylaw footers/noise
                if not content.startswith("City of Airdrie Land Use Bylaw") and not content.startswith("Page "):
                    current_text_parts.append(content)

    # Save the final item
    if current_term and current_text_parts:
        save_definition(converted_definitions, current_term, current_text_parts)

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(converted_definitions, f, indent=2)
    print(f"Success! Converted {len(converted_definitions)} definitions to {output_path}")

def save_definition(output_list, term, text_parts):
    # Clean term of leading artifacts (like 'A-B-C' separators or bullet points)
    clean_term = re.sub(r'^[A-Z]-[A-Z]\s+', '', term).strip()
    
    # Check for empty text parts to avoid saving empty definitions
    full_text = " ".join(text_parts).strip()
    if clean_term and full_text:
        output_list.append({
            "termID": clean_term,
            "terms": clean_term,
            "text": "means: " + full_text,
            "type": "General",
            "image": "",
            "bylaw_id_pointer": ""
        })

# Use raw string (r"") for Windows paths
input_file = r"C:\Users\15877\alberta-airdrie-LUB\scripts\docling_json\Aidrie LUB Definitions Only.json"
output_file = "converted_definitions_only.json"

convert_airdrie_to_standard(input_file, output_file)