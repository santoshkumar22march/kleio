from pydantic import BaseModel

class VerificationCode(BaseModel):
    verification_code: str
