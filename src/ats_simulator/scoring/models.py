from pydantic import BaseModel


class ScoreBreakdown(BaseModel):
    contact_points: int
    sections_points: int
    layout_penalty: int = 0
    table_penalty: int = 0
    low_text_cap_applied: bool = False


class ATSScoreResult(BaseModel):
    score: int
    issues: list[str] = []
    breakdown: ScoreBreakdown
