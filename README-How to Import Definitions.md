# CivicZone: Definition Import Pipeline

This repository contains the three-stage pipeline used to convert raw PDF zoning bylaw definitions into structured, cross-linked definitions within the Payload CMS.
---

1. **PDF Source** -> [input2JSON.py] 
2. **Import Images** -> [smart-img-rip.py]
2. **Docling JSON** -> [cleanJSON.py] 
3. **Standardized JSON** -> [import-definitions.ts] 
4. **Payload CMS (Live)**

---
## Things to install
make sure you have python installed and up to date
"pip install hf_xet" in the command line
AND "pip install pymupdf"

## 📂 Script Breakdown
1. **PDF Source** -> [input2JSON.py] 
Converts PDF to JSON
2. **Import Images** -> [smart-img-rip.py]
Extracts images from PDFs and labels according to definitions
2. **Docling JSON** -> [cleanJSON.py] 
Cleans JSON files and adds image labels to JSON
3. **Standardized JSON** -> [import-definitions.ts] 
Uploads cleaned JSON to CMS

## 🚀 How to Run

1. **Place PDFs** in the `scripts/pdfs` folder.
2. **Run input2JSON.py:**
   python input2JSON.py
   this will put your PDF definitions into a folder scripts/JSON in raw JSON format
3. **Import Images** 
   python smart-image-rip.py
   This will extract images from the PDF and label them according to the definition they came immediately after, if there are multiple it should lable them as such. 
4A **Run Cleaner**
   cleanJSON.py 
   The output will be scripts/JSON/final 
    for each converted file you will need to clean the data, this is a good point to do quality checks for errors
4B **Combine files**
    If there are multiple definition files you can combine them here or you can import then go back to the cleaning stage for each one. 
5. **Run Import**
    npx tsx import-defintions.ts