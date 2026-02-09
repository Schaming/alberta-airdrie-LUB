import json
import os
import re

SEE_PATTERN = re.compile(
    r"^see\s+[\"']?([^\"'.]+)[\"']?\.?$",
    re.IGNORECASE
)

BYLAW_LINE_PATTERN = re.compile(
    r"^Bylaw\s+.+",
    re.IGNORECASE
)

ALL_CAPS_PATTERN = re.compile(r"^[A-Z\s]{5,}$")

def convert_airdrie_to_standard(input_path, output_path):
    if not os.path.exists(input_path):
        print(f"Error: Could not find file at {input_path}")
        return

    with open(input_path, "r", encoding="utf-8") as f:
        source_data = json.load(f)

    texts = source_data.get("texts", [])

    definitions = {}
    alias_map = {}

    current_term = None
    current_text_parts = []
    current_bylaw_pointer = ""

    for item in texts:
        content = item.get("text", "").strip()
        is_bold = item.get("bold", False)

        if not content:
            continue

        # Capture bylaw footer verbatim
        if BYLAW_LINE_PATTERN.match(content):
            current_bylaw_pointer = content
            continue

        # -------------------------
        # BOLD TERM = new definition
        # -------------------------
        if is_bold and not ALL_CAPS_PATTERN.match(content):
            # Save previous definition
            if current_term and current_text_parts:
                save_definition(
                    definitions,
                    alias_map,
                    current_term,
                    current_text_parts,
                    current_bylaw_pointer
                )

            # Clean term
            term = content.rstrip(":").strip()
            current_term = term
            current_text_parts = []
            current_bylaw_pointer = ""
            continue

        # -------------------------
        # Definition body
        # -------------------------
        if current_term:
            # Ignore page numbers
            if content.lower().startswith("page "):
                continue
            current_text_parts.append(content)

    # Save final definition
    if current_term and current_text_parts:
        save_definition(
            definitions,
            alias_map,
            current_term,
            current_text_parts,
            current_bylaw_pointer
        )

    # -------------------------
    # Merge aliases
    # -------------------------
    for alias, target in alias_map.items():
        if target in definitions:
            terms = set(definitions[target]["terms"].split("; "))
            terms.add(alias)
            definitions[target]["terms"] = "; ".join(sorted(terms))

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(list(definitions.values()), f, indent=2)

    print(f"Success! Converted {len(definitions)} definitions to {output_path}")

def save_definition(definitions, alias_map, term, text_parts, bylaw_pointer):
    full_text = " ".join(text_parts).strip()

    # Normalize leading "means"
    full_text = re.sub(r"^means\s*:", "", full_text, flags=re.IGNORECASE).strip()

    # Skip deleted definitions
    if full_text.lower() == "deleted":
        return

    # Alias handling
    see_match = SEE_PATTERN.match(full_text)
    if see_match:
        target = see_match.group(1).strip()
        alias_map[term] = target
        return

    definitions[term] = {
        "termID": term,
        "terms": term,
        "text": "means: " + full_text,
        "type": "General",
        "image": "",
        "bylaw_id_pointer": bylaw_pointer
    }

# -------------------------
# Run
# -------------------------

input_file = r"C:\Users\15877\alberta-airdrie-LUB\scripts\docling_json\Aidrie LUB Definitions Only.json"
output_file = "converted_definitions_only.json"

convert_airdrie_to_standard(input_file, output_file)
