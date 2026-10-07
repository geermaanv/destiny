import json

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from fastapi.responses import PlainTextResponse
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.whatsapp import extract_text_messages, is_mock_mode, process_incoming, signature_is_valid

router = APIRouter(prefix="/webhooks/whatsapp", tags=["whatsapp"])


@router.get("", response_class=PlainTextResponse)
def verify_webhook(
    mode: str = Query(alias="hub.mode"),
    token: str = Query(alias="hub.verify_token"),
    challenge: str = Query(alias="hub.challenge"),
) -> str:
    # Handshake de Meta al configurar el webhook.
    if mode != "subscribe" or not settings.whatsapp_verify_token or token != settings.whatsapp_verify_token:
        raise HTTPException(status_code=403, detail="Invalid verify token")
    return challenge


@router.post("")
async def receive_webhook(request: Request, db: Session = Depends(get_db)) -> dict[str, str]:
    raw_body = await request.body()
    if not is_mock_mode() and not signature_is_valid(raw_body, request.headers.get("X-Hub-Signature-256")):
        raise HTTPException(status_code=403, detail="Invalid signature")

    try:
        payload = json.loads(raw_body)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON")

    for sender, text in extract_text_messages(payload):
        process_incoming(db, sender, text)

    # Meta reintenta si no recibe 200: siempre responder ok una vez validada la firma.
    return {"status": "ok"}
