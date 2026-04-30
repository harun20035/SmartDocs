from app.models.document import Document


def create_document(session, file_name: str, file_path: str):
    document = Document(
        file_name=file_name,
        file_path=file_path,
        status="uploaded"
    )

    session.add(document)
    session.commit()
    session.refresh(document)

    return document


def get_by_id(session, document_id: int):
    return session.query(Document).filter(Document.id == document_id).first()

def get_all(session):
    return session.query(Document).order_by(Document.created_at.desc(), Document.id.desc()).all()


def get_page(session, offset: int, limit: int):
    return (
        session.query(Document)
        .order_by(Document.created_at.desc(), Document.id.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )


def count_all(session):
    return session.query(Document).count()


def update_document(session, document, data: dict):
    for field in [
        "document_type",
        "document_number",
        "supplier_name",
        "issue_date",
        "due_date",
        "currency",
        "subtotal",
        "tax",
        "total",
        "status",
    ]:
        if field in data:
            setattr(document, field, data[field])

    session.commit()
    session.refresh(document)

    return document