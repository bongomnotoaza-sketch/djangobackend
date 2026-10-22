# services.py

import instructor
from django.conf import settings
from instructor.v2.core.errors import InstructorRetryException

from .schemas import IntentResponse
from .prompts import SYSTEM_PROMPT, FEW_SHOT
from .exceptions import IntentClassificationFailed


class IntentClarifierService:

    def __init__(self, model_name: str | None = None):
        self.client = instructor.from_provider(
            model_name or getattr(
                settings,
                "INTENT_MODEL",
                "ollama/gemma2:2b"
            )
        )

    def clarify(self, user_input: str) -> IntentResponse:
        try:
            result = self.client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": SYSTEM_PROMPT,
                    },
                    *FEW_SHOT,
                    {
                        "role": "user",
                        "content": user_input,
                    },
                ],
                response_model=IntentResponse,
                max_retries=2,
                temperature=0,
            )

            return result

        except InstructorRetryException as e:
            raise IntentClassificationFailed(str(e)) from e


# Module-level singleton
# Created once when Django imports this module and reused
# across requests.
intent_clarifier_service = IntentClarifierService()