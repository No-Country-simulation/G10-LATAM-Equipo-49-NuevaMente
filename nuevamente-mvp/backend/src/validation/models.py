from typing import Literal
from pydantic import BaseModel


class Claim(BaseModel):
    id: str
    text: str


class ClaimEvaluation(BaseModel):
    claim_id: str
    claim_text: str
    verdict: Literal["SI", "PARCIAL", "NO"]
    source_chunk_ids: list[str] = []


class FidelityEvaluation(BaseModel):
    score: float | None
    claims: list[ClaimEvaluation]
    claims_no_soportados: list[str]
    observaciones: list[str]
