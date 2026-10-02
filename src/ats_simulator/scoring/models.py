from pydantic import BaseModel


class ATSScoreResult(BaseModel):
    score: int
    issues: list[str] = []
