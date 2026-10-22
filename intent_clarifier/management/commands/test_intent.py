from django.core.management.base import BaseCommand

from intent_classifier.services import intent_classifier_service
from intent_classifier.exceptions import IntentClassificationFailed


class Command(BaseCommand):
    help = "Interactive REPL to manually test the intent classifier service."

    def handle(self, *args, **options):
        self.stdout.write("Intent classifier test REPL. Type 'exit' to quit.\n")

        while True:
            user_input = input("\nEnter your query (or 'exit' to quit): ")

            if user_input.lower() == "exit":
                break

            try:
                result = intent_classifier_service.classify(user_input)
            except IntentClassificationFailed:
                self.stdout.write(self.style.WARNING(
                    "Couldn't understand that query, please rephrase."
                ))
                continue

            for i, req in enumerate(result.requests, start=1):
                label = f" ({i})" if len(result.requests) > 1 else ""
                if req.intent == "unclear" or req.lesson_name == "unclear":
                    self.stdout.write(
                        f"Sorry, I didn't understand that part{label} of your query."
                    )
                    continue
                self.stdout.write(f"Intent{label}: {req.intent}")
                self.stdout.write(f"Lesson{label}: {req.lesson_name}")