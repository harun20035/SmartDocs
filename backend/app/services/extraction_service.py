import csv
import io
import re
from datetime import date
from pathlib import Path


def to_int(value, default=0):
    try:
        return int(str(value).strip())
    except (ValueError, TypeError):
        return default


def to_float(value, default=0.0):
    try:
        return float(str(value).strip().replace(",", "."))
    except (ValueError, TypeError):
        return default


def parse_date(value):
    if not value:
        return None
    raw = str(value).strip()
    for fmt in ("%Y-%m-%d", "%d.%m.%Y", "%d/%m/%Y"):
        try:
            if fmt == "%Y-%m-%d":
                return date.fromisoformat(raw)
            if fmt == "%d.%m.%Y":
                day, month, year = raw.split(".")
                return date(int(year), int(month), int(day))
            if fmt == "%d/%m/%Y":
                day, month, year = raw.split("/")
                return date(int(year), int(month), int(day))
        except (ValueError, TypeError):
            continue
    return None


def extract_label_value(content, label):
    pattern = rf"{label}\s*:\s*(.+)"
    match = re.search(pattern, content, re.IGNORECASE)
    return match.group(1).strip() if match else None


def extract_csv(file_obj):
    content = file_obj.read().decode("utf-8")
    reader = csv.DictReader(io.StringIO(content))

    line_items = []
    for row in reader:
        line_items.append({
            "description": row.get("desc"),
            "quantity": int(row.get("qty", 0)),
            "unit_price": float(row.get("price", 0)),
            "total": float(row.get("total", 0)),
        })

    subtotal = sum(item["total"] for item in line_items)
    return {
        "document_type": "invoice",
        "supplier_name": None,
        "document_number": None,
        "issue_date": None,
        "due_date": None,
        "currency": "EUR",
        "line_items": line_items,
        "subtotal": subtotal,
        "tax": 0.0,
        "total": subtotal,
    }


def extract_txt(file_obj, filename: str):
    content = file_obj.read().decode("utf-8", errors="ignore")
    return extract_text_content(content, filename)


def extract_pdf(file_obj, filename: str):
    try:
        from pypdf import PdfReader
    except ImportError:
        return {
            "error": "PDF support is not installed. Install dependency: pypdf"
        }

    try:
        reader = PdfReader(file_obj)
    except Exception:
        return {
            "error": "Could not read PDF file. The file may be corrupted or encrypted."
        }

    pages_text = []
    for page in reader.pages:
        try:
            pages_text.append(page.extract_text() or "")
        except Exception:
            pages_text.append("")

    content = "\n".join(pages_text).strip()
    if not content:
        return {
            "error": "No readable text found in PDF. OCR is required for scanned/image PDFs."
        }

    return extract_text_content(content, filename)


def extract_text_content(content: str, filename: str):
    if not content or not content.strip():
        return {"error": "Document is empty or unreadable"}

    document_type = extract_label_value(content, "document type") or "invoice"
    supplier_name = extract_label_value(content, "supplier")
    document_number = extract_label_value(content, "document number") or Path(filename).stem
    issue_date = parse_date(extract_label_value(content, "issue date"))
    due_date = parse_date(extract_label_value(content, "due date"))
    currency = extract_label_value(content, "currency") or "EUR"

    subtotal = to_float(extract_label_value(content, "subtotal"))
    tax = to_float(extract_label_value(content, "tax"))
    total = to_float(extract_label_value(content, "total"))

    line_items = []
    # Accepts lines like: "Item A,2,10,20" or "Item A | 2 | 10 | 20"
    for raw_line in content.splitlines():
        line = raw_line.strip()
        if not line or ":" in line:
            continue

        parts = re.split(r"\s*[,\|]\s*", line)
        if len(parts) != 4:
            continue

        qty = to_int(parts[1], default=-1)
        unit_price = to_float(parts[2], default=-1.0)
        line_total = to_float(parts[3], default=-1.0)
        if qty < 0 or unit_price < 0 or line_total < 0:
            continue

        line_items.append(
            {
                "description": parts[0],
                "quantity": qty,
                "unit_price": unit_price,
                "total": line_total,
            }
        )

    # If totals are missing in TXT, derive them from parsed line items.
    derived_subtotal = sum(item["total"] for item in line_items)
    if subtotal == 0 and line_items:
        subtotal = derived_subtotal
    if total == 0 and line_items:
        total = subtotal + tax

    return {
        "document_type": document_type.lower(),
        "supplier_name": supplier_name,
        "document_number": document_number,
        "issue_date": issue_date,
        "due_date": due_date,
        "currency": currency.upper(),
        "line_items": line_items,
        "subtotal": subtotal,
        "tax": tax,
        "total": total,
    }


def extract(file_obj, filename: str):
    filename = filename.lower()

    if filename.endswith(".csv"):
        extracted = extract_csv(file_obj)
        extracted["document_number"] = Path(filename).stem
        return extracted
    if filename.endswith(".txt"):
        return extract_txt(file_obj, filename)
    if filename.endswith(".pdf"):
        return extract_pdf(file_obj, filename)

    return {
        "error": "Unsupported file type. Supported formats are: .csv, .txt, .pdf"
    }