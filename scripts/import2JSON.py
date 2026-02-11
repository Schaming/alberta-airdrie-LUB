import json
import os
import re
from docling.document_converter import DocumentConverter

# --- CONFIGURATION ---
INPUT_FOLDER = r"C:\Users\15877\alberta-airdrie-LUB\scripts\pdfs"
OUTPUT_FOLDER = r"C:\Users\15877\alberta-airdrie-LUB\scripts\JSON"
IMAGE_FOLDER = r"C:\Users\15877\alberta-airdrie-LUB\scripts\JSON\images"

def normalize_glyph(text):
    """ Standardizes LUB artifacts while keeping Markdown intact """
    if not text:
        return text
    # Standardize bullet markers
    if text.strip().lower() == "x":
        return "•"
    return text

def export_raw_docling_data():
    if not os.path.exists(OUTPUT_FOLDER): os.makedirs(OUTPUT_FOLDER)
    if not os.path.exists(IMAGE_FOLDER): os.makedirs(IMAGE_FOLDER)
    
    print("Initializing Docling: Importing Rich Text to Raw JSON...")
    converter = DocumentConverter()
    pdf_files = [f for f in os.listdir(INPUT_FOLDER) if f.lower().endswith('.pdf')]
    
    for filename in pdf_files:
        input_path = os.path.join(INPUT_FOLDER, filename)
        output_path = os.path.join(OUTPUT_FOLDER, os.path.splitext(filename)[0] + "_RAW.json")
        print(f"--- Processing: {filename} ---")
        
        try:
            result = converter.convert(input_path)
            raw_elements = []
            img_count = 0
            doc = result.document

            for item, _ in doc.iterate_items():
                
                # 1. HANDLE TABLES (Rich Text / Markdown support)
                if hasattr(item, "data") and hasattr(item, "export_to_dataframe"):
                    try:
                        df = item.export_to_dataframe(doc) 
                        for _, row in df.iterrows():
                            # Preserves cell strings (Markdown)
                            clean_cells = [normalize_glyph(str(cell).strip()) for cell in row.values]
                            raw_elements.append({
                                "type": "table_row",
                                "cells": clean_cells
                            })
                        continue 
                    except Exception as e:
                        print(f"      Table Error: {e}")

                # 2. HANDLE IMAGES
                if hasattr(item, "image") and item.image:
                    img_count += 1
                    img_name = f"{os.path.splitext(filename)[0]}_img_{img_count}.png"
                    img_path = os.path.join(IMAGE_FOLDER, img_name)
                    item.image.pil_image.save(img_path)
                    
                    raw_elements.append({
                        "type": "image",
                        "image_path": img_name
                    })
                
                # 3. HANDLE TEXT (The "Rich Text" Logic)
                if hasattr(item, "text") and item.text.strip():
                    try:
                        # CRITICAL: This extracts the specific item with its bold/italic markers
                        rich_content = doc.export_to_markdown(item_set=[item])
                        content = normalize_glyph(rich_content.strip())
                        
                        element = {
                            "type": "text",
                            "content": content # This is now 'Rich Text' inside the JSON
                        }
                        
                        if hasattr(item, "prov") and item.prov:
                            bbox = item.prov[0].bbox
                            element["coords"] = {
                                "l": round(bbox.l, 2), "t": round(bbox.t, 2), 
                                "r": round(bbox.r, 2), "b": round(bbox.b, 2)
                            }
                        
                        raw_elements.append(element)
                    except:
                        # Fallback if markdown export glitches
                        raw_elements.append({"type": "text", "content": item.text.strip()})

            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(raw_elements, f, indent=2)
            print(f"   Success! Created Raw JSON with Rich Text.")

        except Exception as e:
            print(f"   Critical Error on {filename}: {e}")

if __name__ == "__main__":
    export_raw_docling_data()