from fastapi import HTTPException
from app.repositories.document_repository import create_document, get_by_id
from app.services.extraction_service import extract
import os
from datetime import date
from app.services.validation_service import validate_extracted_data
from app.models.line_item import LineItem
from app.models.validation_error import ValidationError

UPLOAD_DIR = "uploads"


def parse_optional_date(value):
    if value in (None, ""):
        return None
    if isinstance(value, date):
        return value
    text = str(value).strip()
    try:
        return date.fromisoformat(text)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid date format: {value}")


def process_uploaded_file(session, file):
    if not file.filename:
        raise HTTPException(status_code=400, detail="File is required")

    os.makedirs(UPLOAD_DIR, exist_ok=True)

    file_path = os.path.join(UPLOAD_DIR, file.filename)

    with open(file_path, "wb") as buffer:
        buffer.write(file.file.read())

    document = create_document(
        session=session,
        file_name=file.filename,
        file_path=file_path
    )

    return {
        "id": document.id,
        "file_name": document.file_name,
        "status": document.status
    }

def process_document(session, document_id: int):
    document = get_by_id(session, document_id)

    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    # 1. Extract
    with open(document.file_path, "rb") as f:
        extracted_data = extract(f, document.file_name)

    if extracted_data.get("error"):
        raise HTTPException(status_code=400, detail=extracted_data["error"])

    # 2. Persist extracted header fields
    if "document_type" in extracted_data:
        document.document_type = extracted_data.get("document_type")
    if "supplier_name" in extracted_data:
        document.supplier_name = extracted_data.get("supplier_name")
    if "document_number" in extracted_data:
        document.document_number = extracted_data.get("document_number")
    if "issue_date" in extracted_data:
        document.issue_date = extracted_data.get("issue_date")
    if "due_date" in extracted_data:
        document.due_date = extracted_data.get("due_date")
    if "currency" in extracted_data:
        document.currency = extracted_data.get("currency")

    document.subtotal = extracted_data.get("subtotal")
    document.tax = extracted_data.get("tax")
    document.total = extracted_data.get("total")

    # 3. Replace line items with newly extracted ones
    session.query(LineItem).filter(LineItem.document_id == document.id).delete()
    for item in extracted_data.get("line_items", []):
        session.add(
            LineItem(
                document_id=document.id,
                description=item.get("description"),
                quantity=item.get("quantity"),
                unit_price=item.get("unit_price"),
                total=item.get("total"),
            )
        )

    # 4. Clear previous validation errors before re-validating
    session.query(ValidationError).filter(
        ValidationError.document_id == document.id
    ).delete()

    # 2. Validate
    validation = validate_extracted_data(session, document, extracted_data)

    # 5. Status workflow
    if validation["is_valid"]:
        document.status = "validated"
    else:
        document.status = "needs_review"

    session.commit()
    session.refresh(document)

    # 6. Return response
    return {
        "document_id": document.id,
        "file_name": document.file_name,
        "status": document.status,
        "extracted_data": extracted_data,
        "validation": validation
    }

def get_document_detail(session, document_id: int):
    document = get_by_id(session, document_id)

    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    return {
        "id": document.id,
        "file_name": document.file_name,
        "status": document.status,
        "document_type": document.document_type,
        "document_number": document.document_number,
        "supplier_name": document.supplier_name,
        "issue_date": document.issue_date,
        "due_date": document.due_date,
        "currency": document.currency,
        "subtotal": document.subtotal,
        "tax": document.tax,
        "total": document.total,

        "line_items": [
            {
                "description": li.description,
                "quantity": li.quantity,
                "unit_price": li.unit_price,
                "total": li.total
            }
            for li in document.line_items
        ],

        "validation_errors": [
            {
                "type": err.error_type,
                "field": err.field_name,
                "message": err.message
            }
            for err in document.validation_errors
        ]
    }

def update_document_service(session, document_id: int, data: dict):
    document = get_by_id(session, document_id)

    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    # 1. Update basic fields
    updatable_fields = [
        "document_type",
        "document_number",
        "supplier_name",
        "currency",
        "subtotal",
        "tax",
        "total",
    ]
    for field in updatable_fields:
        if field in data:
            setattr(document, field, data[field])
    if "issue_date" in data:
        document.issue_date = parse_optional_date(data.get("issue_date"))
    if "due_date" in data:
        document.due_date = parse_optional_date(data.get("due_date"))

    # 2. Replace line items when sent from UI
    if "line_items" in data:
        session.query(LineItem).filter(LineItem.document_id == document.id).delete()
        for item in data.get("line_items", []):
            session.add(
                LineItem(
                    document_id=document.id,
                    description=item.get("description"),
                    quantity=item.get("quantity"),
                    unit_price=item.get("unit_price"),
                    total=item.get("total"),
                )
            )

    # 3. Clear old validation errors
    session.query(ValidationError).filter(
        ValidationError.document_id == document.id
    ).delete()

    # 4. Rebuild extracted-like data from current DB values, then validate
    current_line_items = data.get("line_items")
    if current_line_items is None:
        current_line_items = [
            {
                "description": li.description,
                "quantity": li.quantity,
                "unit_price": li.unit_price,
                "total": li.total,
            }
            for li in session.query(LineItem).filter(LineItem.document_id == document.id).all()
        ]
    extracted_data = {"line_items": current_line_items}
    validation = validate_extracted_data(session, document, extracted_data)

    requested_status = data.get("status")

    # 5. Workflow rules
    if requested_status == "rejected":
        document.status = "rejected"
    elif requested_status == "validated":
        if not validation["is_valid"]:
            raise HTTPException(
                status_code=400,
                detail="Cannot confirm document while validation errors exist",
            )
        document.status = "validated"
    else:
        document.status = "validated" if validation["is_valid"] else "needs_review"

    session.commit()
    session.refresh(document)

    return {
        "id": document.id,
        "status": document.status,
        "validation": validation,
    }