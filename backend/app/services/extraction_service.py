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
    if value is None:
        return default
    try:
        cleaned = re.sub(r"[^\d.,\-]", "", str(value).strip())
        cleaned = cleaned.replace(",", ".")
        return float(cleaned) if cleaned else default
    except (ValueError, TypeError):
        return default


def parse_date(value):
    if not value:
        return None
    raw = str(value).strip()
    parts = re.split(r"[-./]", raw)
    try:
        if len(parts) == 3 and len(parts[0]) == 4:
            return date(int(parts[0]), int(parts[1]), int(parts[2]))
        if len(parts) == 3 and len(parts[2]) == 4:
            return date(int(parts[2]), int(parts[1]), int(parts[0]))
    except (ValueError, TypeError):
        return None


def extract_label_value(content, label):
    aliases = {
        "supplier":        ["supplier", "supplier name", "vendor", "company", "from"],
        "document number": ["document number", "doc number", "number", "invoice no",
                            "invoice number", "po number", "order number"],
        "issue date":      ["issue date", "date", "invoice date", "issued"],
        "due date":        ["due date", "due", "payment due", "pay by"],
        "document type":   ["document type", "doc type", "type"],
        "currency":        ["currency", "cur"],
        "subtotal":        ["subtotal", "sub total", "net total"],
        "tax":             ["tax", "vat", "gst"],
        "total":           ["total", "grand total", "amount due", "total due"],
    }

    search_labels = aliases.get(label.lower(), [label])
    for lbl in search_labels:
        pattern = rf"(?im)^[ \t]*{re.escape(lbl)}\s*[:\-]\s*(.+)"
        match = re.search(pattern, content)
        if match:
            return match.group(1).strip()
    return None


def extract_currency(content: str):
    currency_re = re.compile(
        r"\b(EUR|USD|GBP|BAM|CHF|HRK|RSD|DKK|SEK|NOK|CAD|AUD)\b|([€$£])",
        re.IGNORECASE,
    )
    symbol_map = {"€": "EUR", "$": "USD", "£": "GBP"}

    explicit = extract_label_value(content, "currency")
    if explicit:
        m = currency_re.search(explicit)
        if m:
            return (m.group(1) or symbol_map.get(m.group(2), "EUR")).upper()

    for line in content.splitlines():
        if re.search(r"(?i)(total|subtotal|amount|price)", line):
            m = currency_re.search(line)
            if m:
                return (m.group(1) or symbol_map.get(m.group(2), "EUR")).upper()

    return "EUR"


def extract_csv(file_obj):
    content = file_obj.read().decode("utf-8")
    reader = csv.DictReader(io.StringIO(content))

    line_items = []
    for row in reader:
        line_items.append({
            "description": row.get("desc") or row.get("description", ""),
            "quantity": to_int(row.get("qty", 0)),
            "unit_price": to_float(row.get("price", 0)),
            "total": to_float(row.get("total", 0)),
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


def extract_text_content(content: str, filename: str):
    if not content or not content.strip():
        return {"error": "Document is empty or unreadable"}

    document_type   = (extract_label_value(content, "document type") or "invoice").lower()
    supplier_name   = extract_label_value(content, "supplier")
    document_number = extract_label_value(content, "document number") or Path(filename).stem
    issue_date      = parse_date(extract_label_value(content, "issue date"))
    due_date        = parse_date(extract_label_value(content, "due date"))
    currency        = extract_currency(content)
    subtotal        = to_float(extract_label_value(content, "subtotal"))
    tax             = to_float(extract_label_value(content, "tax"))
    total           = to_float(extract_label_value(content, "total"))

    line_items = []
    for raw_line in content.splitlines():
        line = raw_line.strip()
        if not line or ":" in line:
            continue

        parts = re.split(r"\s*[,\|]\s*", line)
        if len(parts) != 4:
            continue

        qty        = to_int(parts[1], default=-1)
        unit_price = to_float(parts[2], default=-1.0)
        line_total = to_float(parts[3], default=-1.0)
        if qty < 0 or unit_price < 0 or line_total < 0:
            continue

        line_items.append({
            "description": parts[0],
            "quantity":    qty,
            "unit_price":  unit_price,
            "total":       line_total,
        })

    derived_subtotal = sum(item["total"] for item in line_items)
    if subtotal == 0 and line_items:
        subtotal = derived_subtotal
    if total == 0 and line_items:
        total = subtotal + tax

    return {
        "document_type":   document_type,
        "supplier_name":   supplier_name,
        "document_number": document_number,
        "issue_date":      issue_date,
        "due_date":        due_date,
        "currency":        currency,
        "line_items":      line_items,
        "subtotal":        subtotal,
        "tax":             tax,
        "total":           total,
    }


SUMMARY_LABELS = {
    "subtotal", "sub total", "tax", "vat", "gst",
    "total", "grand total", "amount due", "total due",
}


def extract_pdf(file_obj, filename: str):
    try:
        import pdfplumber
    except ImportError:
        return {"error": "pdfplumber nije instaliran. Pokreni: pip install pdfplumber"}

    try:
        pdf = pdfplumber.open(file_obj)
    except Exception:
        return {"error": "Ne mogu otvoriti PDF. Fajl je možda oštećen ili enkriptovan."}

    with pdf:
        all_text_parts = []
        all_tables = []
        for page in pdf.pages:
            all_text_parts.append(page.extract_text() or "")
            all_tables.extend(page.extract_tables())

    text = "\n".join(all_text_parts).strip()
    if not text and not all_tables:
        return {"error": "PDF ne sadrži čitljiv tekst. Potreban OCR za skenirane dokumente."}

    result = {
        "document_type":   (extract_label_value(text, "document type") or "invoice").lower(),
        "supplier_name":   extract_label_value(text, "supplier"),
        "document_number": extract_label_value(text, "document number"),
        "issue_date":      parse_date(extract_label_value(text, "issue date")),
        "due_date":        parse_date(extract_label_value(text, "due date")),
        "currency":        extract_currency(text),
        "line_items":      [],
        "subtotal":        0.0,
        "tax":             0.0,
        "total":           0.0,
    }

    for table in all_tables:
        if not table:
            continue

        header_idx = 0
        for i, row in enumerate(table):
            row_text = " ".join(str(c or "").lower() for c in row)
            if re.search(r"\b(description|item|service|qty|quantity)\b", row_text):
                header_idx = i
                break

        for row in table[header_idx + 1:]:
            if not row or len(row) < 2:
                continue

            cells = [str(c).strip() if c else "" for c in row]
            full_label = re.sub(r"\s*\(.*?\)", "", " ".join(cells).lower()).strip()

            matched_summary = next(
                (sl for sl in SUMMARY_LABELS if sl in full_label), None
            )

            if matched_summary:
                numeric_val = to_float(next(
                    (c for c in reversed(cells) if re.search(r"\d", c)), "0"
                ))
                if "subtotal" in matched_summary or "sub total" in matched_summary:
                    result["subtotal"] = numeric_val
                elif "tax" in matched_summary or "vat" in matched_summary:
                    result["tax"] = numeric_val
                elif "total" in matched_summary:
                    result["total"] = numeric_val
                continue

            desc = cells[0]
            if not desc:
                continue

            numeric_cells = [c for c in cells[1:] if re.search(r"\d", c)]
            if not numeric_cells:
                continue

            if len(numeric_cells) >= 3:
                qty        = to_int(numeric_cells[-3])
                unit_price = to_float(numeric_cells[-2])
                line_total = to_float(numeric_cells[-1])
            elif len(numeric_cells) == 2:
                qty        = to_int(numeric_cells[0])
                unit_price = 0.0
                line_total = to_float(numeric_cells[1])
            else:
                qty        = 1
                unit_price = 0.0
                line_total = to_float(numeric_cells[0])

            result["line_items"].append({
                "description": desc,
                "quantity":    qty,
                "unit_price":  unit_price,
                "total":       line_total,
            })

    if result["subtotal"] == 0.0 and result["line_items"]:
        result["subtotal"] = sum(i["total"] for i in result["line_items"])
    if result["total"] == 0.0:
        result["total"] = result["subtotal"] + result["tax"]
    if not result["document_number"]:
        result["document_number"] = Path(filename).stem

    return result


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

    return {"error": "Unsupported file type. Supported formats are: .csv, .txt, .pdf"}