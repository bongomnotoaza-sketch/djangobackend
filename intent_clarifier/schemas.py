from pydantic import BaseModel, field_validator
from typing import List, Literal

LessonName = Literal["biology", "mathematics", "chemistry", "physics", "english", "unclear"]

class LessonRequest(BaseModel):
    intent: Literal["get_lesson_date", "get_lesson_teacher", "get_lesson_notes", "unclear"]
    lesson_name: LessonName

    @field_validator("lesson_name", mode="before")
    @classmethod
    def clean_lesson_name(cls, v):
        if not isinstance(v, str):
            return v
        v = v.strip().strip('"').strip("'").lower()
        known = {"biology", "mathematics", "chemistry", "physics", "english", "unclear"}
        return v if v in known else "unclear"

class IntentResponse(BaseModel):
    requests: List[LessonRequest]