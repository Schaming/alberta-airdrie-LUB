from docling.document_converter import DocumentConverter
from pathlib import Path
import json

def pdf_to_docling_json(pdf_path: str, converter: DocumentConverter, output_dir="docling"):
    """
    Converts a single PDF to a Docling JSON file. 
    Accepts an existing converter instance to save memory/time.
    """
    pdf_path = Path(pdf_path)

    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF not found: {pdf_path.resolve()}")

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"[INFO] Converting PDF: {pdf_path.name}...")

    # Reuse the passed converter
    result = converter.convert(str(pdf_path))
    doc = result.document

    # Export to dict
    json_obj = doc.model_dump()
    json_obj["metadata"] = {"source_file": str(pdf_path.resolve())}

    output_path = output_dir / (pdf_path.stem + ".json")

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(json_obj, f, indent=2)

    print(f"[SUCCESS] Saved Docling JSON: {output_path.resolve()}")
    return output_path


def batch_convert_folder(pdf_folder: str, output_dir="docling"):
    pdf_folder = Path(pdf_folder)
    if not pdf_folder.exists() or not pdf_folder.is_dir():
        raise FileNotFoundError(f"PDF folder not found: {pdf_folder.resolve()}")

    pdf_files = list(pdf_folder.glob("*.pdf"))
    if not pdf_files:
        print(f"[INFO] No PDF files found in folder: {pdf_folder.resolve()}")
        return

    # Initialize the converter ONCE here
    print("[INFO] Initializing Docling models...")
    converter = DocumentConverter()

    for pdf_file in pdf_files:
        try:
            pdf_to_docling_json(pdf_file, converter, output_dir)
        except Exception as e:
            print(f"[ERROR] Failed to convert {pdf_file.name}: {e}")


if __name__ == "__main__":
    batch_convert_folder(
        r"C:\Users\15877\alberta-airdrie-LUB\scripts\pdfs", 
        output_dir="docling_json"
    )