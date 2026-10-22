from django.shortcuts import render

import json
import logging

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from .services import IntentClarifierService
from .exceptions import IntentClassificationFailed

logger = logging.getLogger("intent_clarifier")


@csrf_exempt  # No auth/CSRF handling yet — fine for local testing only,
              # revisit before this is exposed anywhere real.
@require_POST
def classify_intent(request):
    try:
        body = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON body"}, status=400)

    query = body.get("query", "").strip()
    if not query:
        return JsonResponse({"error": "Missing 'query' field"}, status=400)

    try:
        result = intent_classifier_service.classify(query)
    except IntentClassificationFailed:
        logger.warning("Could not classify query: %r", query)
        return JsonResponse({"status": "failed"}, status=422)

    # Log the result server-side only — this endpoint doesn't expose the
    # classification data to whoever calls it, since it's meant to be
    # consumed by another backend service, not a browser/frontend.
    logger.info(
        "Classified query %r -> %s",
        query,
        [req.model_dump() for req in result.requests],
    )

    return JsonResponse({"status": "ok"})
