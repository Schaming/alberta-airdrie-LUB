# CivicZone: Definition Import Pipeline

This repository contains the three-stage pipeline used to convert raw PDF zoning bylaw definitions into structured, cross-linked definitions within the Payload CMS.
---

1. **PDF Source** -> [docling2JSON.py] 
2. **Docling JSON** -> [cleanJSON.py] 
3. **Standardized JSON** -> [import-definitions.ts] 
4. **Payload CMS (Live)**

---
## Things to install
make sure you have python installed and up to date
also install "pip install hf_xet" in the command line

## 📂 Script Breakdown

### 1. Extraction: `docling2JSON.py`
**Purpose:** Converts visual PDF layouts into machine-readable document models.
- **Technology:** Uses `Docling` library.
- **Key Logic:** Initializes a `DocumentConverter` once to process a batch of PDFs (if nessecary, eg. regular definitions section & sign definitions section). It captures the document hierarchy (headings, tables, and paragraphs) rather than just dumping raw text.
- **Input:** `./scripts/pdfs/*.pdf`
- **Output:** `./docling_json/*.json`

### 2. Transformation: `cleanJSON.py`
**Purpose:** Parses the document model into specific "Term" and "Definition" objects.
- **Technology:** Python + Regular Expressions (Regex).
- **Key Logic:** - Uses `means_pattern` to identify the start of a definition.
    - Handles edge cases where one definition ends and another begins in the same block.
    - Strips out persistent "noise" like Bylaw page numbers and footers.
    - Standardizes the data structure for the CMS.
- **Input:** Specific file from `docling_json/`.
- **Output:** `converted_definitions.json`
- **Data Structure** The output data should have termID, terms, text, type and images. For each defintion. 


### 3. Loading & Enrichment: `import-definitions.ts`
**Purpose:** Injects the data into the CMS and automatically generates internal links.
- **Technology:** TypeScript + Payload CMS + Lexical Editor.
- **Key Logic:**
    - **Lexical Conversion:** Converts raw strings into the nested JSON format required by Payload's Lexical rich-text editor.
    - **Smart Linking (`addSpanTags`):** Scans the text of every definition for *other* terms in the database. If a match is found, it wraps it in a `<span class="def-link">`, creating an instant web of cross-referenced data.
    - **De-duplication:** Checks for existing `termID`s in the CMS to decide whether to Create or Update (UPSERT).
- **Input:** `definitions2.json` (The converted output).
- **Output:** Live database entries in `definition-content` and `definitions` collections.

---

## 🚀 How to Run

1. **Place PDFs** in the `scripts/pdfs` folder.
2. **Run Docling:**
   ```bash
   python docling2JSON-convertor.py
3. **Run Cleaner**
    for each converted file you will need to clean the data, this is a good point to do quality checks for errors, adjust script and rerun if data is wrong, if there are few errors adjust manually
3B **Combine files**
    If there are multiple definition files you can combine them here or you can import then go back to the cleaning stage for each one. 
4. **Run Import**
    npx tsx import-defintions.ts