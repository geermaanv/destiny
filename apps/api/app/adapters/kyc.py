import uuid
from dataclasses import dataclass
from typing import Protocol

# Estados posibles de verificación (spec A3-verificacion-identidad.md).
VERIFICATION_STATUSES = ("pendiente", "en_revision", "verificado", "rechazado", "duplicado_detectado")


@dataclass
class VerificationResult:
    verification_id: str
    status: str


class IdentityVerificationAdapter(Protocol):
    def start_verification(self, profile_id: str, media: bytes) -> VerificationResult: ...
    def get_status(self, verification_id: str) -> str: ...


class MockKYCAdapter:
    """Adapter de desarrollo (ADR 0006): no hay vendor de KYC elegido todavía.

    Resuelve sin intervención humana para poder probar el flujo completo.
    Convención de testing: el contenido del archivo manda el resultado
    ("REJECT" -> rechazado, "DUPLICATE" -> duplicado_detectado, vacío ->
    rechazado, cualquier otra cosa -> verificado). Un vendor real reemplaza
    esta clase sin tocar el router ni los modelos.
    """

    def __init__(self) -> None:
        self._results: dict[str, str] = {}

    def start_verification(self, profile_id: str, media: bytes) -> VerificationResult:
        verification_id = str(uuid.uuid4())

        if not media:
            status = "rechazado"
        elif media == b"REJECT":
            status = "rechazado"
        elif media == b"DUPLICATE":
            status = "duplicado_detectado"
        else:
            status = "verificado"

        self._results[verification_id] = status
        return VerificationResult(verification_id=verification_id, status=status)

    def get_status(self, verification_id: str) -> str:
        return self._results.get(verification_id, "pendiente")


def get_kyc_adapter() -> IdentityVerificationAdapter:
    return _default_adapter


_default_adapter = MockKYCAdapter()
