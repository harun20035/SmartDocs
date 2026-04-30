from app.repositories.document_repository import get_page, count_all, get_all
import os


def get_file_type_label(file_name: str):
    ext = os.path.splitext((file_name or "").lower())[1]
    labels = {
        ".txt": "Text File",
        ".csv": "CSV File",
        ".pdf": "PDF File",
        ".png": "Image File",
        ".jpg": "Image File",
        ".jpeg": "Image File",
        ".webp": "Image File",
    }
    return labels.get(ext, "Unknown File")


def get_dashboard(session, offset: int = 0, limit: int = 10):
    documents = get_page(session, offset=offset, limit=limit)
    total = count_all(session)
    all_documents = get_all(session)

    result = []

    for doc in documents:
        result.append({
            "id": doc.id,
            "file_name": doc.file_name,
            "file_type": get_file_type_label(doc.file_name),
            "status": doc.status,

            # placeholder za sada
            "issues": len(doc.validation_errors) if hasattr(doc, "validation_errors") else 0
        })

    totals_by_currency = {}
    for doc in all_documents:
        if doc.currency and doc.total is not None:
            currency = str(doc.currency).upper()
            totals_by_currency[currency] = round(
                totals_by_currency.get(currency, 0.0) + float(doc.total), 2
            )

    return {
        "items": result,
        "total": total,
        "offset": offset,
        "limit": limit,
        "has_more": (offset + len(result)) < total,
        "totals_by_currency": totals_by_currency,
    }