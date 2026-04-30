from fastapi import APIRouter, UploadFile, File
from app.database import SessionDep
from app.services import document_service, extraction_service, validation_service

router = APIRouter(prefix="/documents", tags=["Documents"])


@router.post("/upload")
async def upload_document(session: SessionDep, file: UploadFile = File(...)):
    return document_service.process_uploaded_file(session, file)

@router.post("/{document_id}/process")
def process_document(document_id: int, session: SessionDep):
    return document_service.process_document(session, document_id)

@router.get("/{document_id}")
def get_document(document_id: int, session: SessionDep):
    return document_service.get_document_detail(session, document_id)

@router.put("/{document_id}")
def update_document_endpoint(document_id: int, data: dict, session: SessionDep):
    return document_service.update_document_service(session, document_id, data)