from app.models.validation_error import ValidationError
from datetime import date


def add_error(session, document_id, error_type, field_name, message):
    error = ValidationError(
        document_id=document_id,
        error_type=error_type,
        field_name=field_name,
        message=message
    )
    session.add(error)


def validate_extracted_data(session, document, extracted_data):
    errors = []
    line_items = extracted_data.get("line_items", [])

    # 1. Missing required header fields
    required_fields = {
        "document_type": document.document_type,
        "supplier_name": document.supplier_name,
        "document_number": document.document_number,
        "issue_date": document.issue_date,
        "due_date": document.due_date,
        "currency": document.currency,
        "subtotal": document.subtotal,
        "tax": document.tax,
        "total": document.total,
    }
    for field_name, value in required_fields.items():
        if value in (None, ""):
            msg = f"Missing required field: {field_name}"
            add_error(session, document.id, "MISSING_FIELD", field_name, msg)
            errors.append(msg)

    # 2. Document type validation
    if document.document_type:
        normalized_type = str(document.document_type).strip().lower().replace(" ", "_")
        if normalized_type not in {"invoice", "purchase_order"}:
            msg = "Invalid document type. Use 'invoice' or 'purchase_order'"
            add_error(session, document.id, "INVALID_VALUE", "document_type", msg)
            errors.append(msg)

    # 3. Date validation
    if document.issue_date is not None and not isinstance(document.issue_date, date):
        msg = "Issue date must be a valid date"
        add_error(session, document.id, "INVALID_DATE", "issue_date", msg)
        errors.append(msg)

    if document.due_date is not None and not isinstance(document.due_date, date):
        msg = "Due date must be a valid date"
        add_error(session, document.id, "INVALID_DATE", "due_date", msg)
        errors.append(msg)

    if isinstance(document.issue_date, date) and isinstance(document.due_date, date):
        if document.due_date < document.issue_date:
            msg = "Due date cannot be earlier than issue date"
            add_error(session, document.id, "INVALID_DATE", "due_date", msg)
            errors.append(msg)

    # 4. Missing line items
    if not line_items:
        msg = "No line items found"
        add_error(
            session,
            document.id,
            "MISSING_FIELD",
            "line_items",
            msg
        )
        errors.append(msg)

    # 5. Line item validation
    subtotal = 0
    for item in line_items:
        qty = item.get("quantity") or 0
        price = item.get("unit_price") or 0
        total = item.get("total") or 0
        expected = qty * price

        if abs(expected - total) > 0.01:
            msg = f"Line item mismatch: {item.get('description')}"
            add_error(
                session,
                document.id,
                "MATH_MISMATCH",
                "total",
                msg
            )
            errors.append(msg)

        subtotal += total

    # 6. Subtotal check
    if document.subtotal is not None:
        if abs(subtotal - document.subtotal) > 0.01:
            msg = "Subtotal mismatch"
            add_error(
                session,
                document.id,
                "MATH_MISMATCH",
                "subtotal",
                msg
            )
            errors.append(msg)

    # 7. Total check
    if document.total is not None and document.subtotal is not None:
        expected_total = document.subtotal + (document.tax or 0)
        if abs(expected_total - document.total) > 0.01:
            msg = "Total mismatch"
            add_error(
                session,
                document.id,
                "MATH_MISMATCH",
                "total",
                msg
            )
            errors.append(msg)

    # 8. Duplicate document number
    if document.document_number:
        existing = session.query(type(document)).filter(
            type(document).document_number == document.document_number
        ).first()
        if existing and existing.id != document.id:
            msg = "Duplicate document number"
            add_error(
                session,
                document.id,
                "DUPLICATE",
                "document_number",
                msg
            )
            errors.append(msg)

    return {
        "is_valid": len(errors) == 0,
        "errors": errors
    }