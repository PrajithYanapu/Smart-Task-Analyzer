from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view
from .serializers import TaskInputSerializer
from .scoring import calculate_scores, load_user_weights, WEIGHTS_FILE
import json
import os

###############################################################################
# ANALYZE VIEW
###############################################################################

class AnalyzeTasksView(APIView):
    """
    POST /api/tasks/analyze/
    Body: { "tasks": [ ... ], "weights": {...} (optional), "strategy": "fastest|impact|deadline|smart" (optional) }
    Returns sorted tasks with scores and explanation, plus cycle detection info.
    """
    def post(self, request):
        payload = request.data or {}
        tasks = payload.get('tasks') or []
        weights = payload.get('weights')
        strategy = payload.get('strategy')

        if not isinstance(tasks, list):
            return Response({"detail": "tasks must be a list"}, status=status.HTTP_400_BAD_REQUEST)

        # Validate tasks
        validated = []
        errors = []
        for i, t in enumerate(tasks):
            s = TaskInputSerializer(data=t)
            if s.is_valid():
                validated.append(s.validated_data)
            else:
                errors.append({'index': i, 'errors': s.errors})

        if errors:
            return Response({'detail': 'validation_error', 'errors': errors},
                            status=status.HTTP_400_BAD_REQUEST)

        result = calculate_scores(validated, weights=weights, strategy=strategy)

        if result['cycles']:
            return Response({
                'warning': 'circular_dependencies_detected',
                'cycles': result['cycles'],
                'result': result
            }, status=status.HTTP_200_OK)

        return Response(result, status=status.HTTP_200_OK)


###############################################################################
# SUGGEST VIEW
###############################################################################

@api_view(['GET'])
def suggest_tasks(request):
    """
    GET /api/tasks/suggest/
    Params: tasks=[...] (JSON), strategy=str, weights={}
    Returns top 3 suggestion tasks.
    """
    tasks_param = request.query_params.get('tasks')
    strategy = request.query_params.get('strategy')
    weights_param = request.query_params.get('weights')

    # Parse tasks
    try:
        tasks = json.loads(tasks_param) if tasks_param else []
    except Exception:
        return Response({'detail': 'invalid tasks JSON'}, status=status.HTTP_400_BAD_REQUEST)

    # Parse weights
    try:
        weights = json.loads(weights_param) if weights_param else None
    except Exception:
        weights = None

    # Validate tasks
    validated = []
    errors = []
    for i, t in enumerate(tasks):
        s = TaskInputSerializer(data=t)
        if s.is_valid():
            validated.append(s.validated_data)
        else:
            errors.append({'index': i, 'errors': s.errors})

    if errors:
        return Response({'detail': 'validation_error', 'errors': errors},
                        status=status.HTTP_400_BAD_REQUEST)

    result = calculate_scores(validated, weights=weights, strategy=strategy)
    top3 = result['tasks'][:3]

    suggestions = [{
        'id': t['id'],
        'title': t['title'],
        'score': t['score'],
        'explanation': t['reason'],
    } for t in top3]

    return Response({
        'suggestions': suggestions,
        'cycles': result['cycles'],
    }, status=200)


###############################################################################
# BONUS: DEPENDENCY GRAPH
###############################################################################

@api_view(["POST"])
def task_graph(request):
    """
    POST /api/tasks/graph/
    Body: { "tasks": [...] }
    Returns a dependency graph for visualization.
    """
    tasks = request.data.get("tasks", [])

    nodes = []
    edges = []

    for t in tasks:
        nodes.append({"id": t["id"], "label": t["title"]})
        for dep in t.get("dependencies", []):
            edges.append({"from": dep, "to": t["id"]})

    return Response({"nodes": nodes, "edges": edges})


###############################################################################
# BONUS: LEARNING SYSTEM FEEDBACK
###############################################################################

def save_user_weights(w):
    with open(WEIGHTS_FILE, "w") as f:
        json.dump(w, f)


@api_view(["POST"])
def feedback(request):
    """
    POST /api/tasks/feedback/
    Body: { "selected": ["id1","id2"], "helpful": true/false }
    Adjusts scoring weights based on whether suggestions were helpful.
    """
    selected = request.data.get("selected", [])
    helpful = request.data.get("helpful", True)

    weights = load_user_weights()

    # Simple learning logic:
    # If user says helpful -> boost urgency & importance slightly
    # If not helpful       -> reduce them slightly (down to a floor)
    delta = 0.02 * len(selected) if selected else 0.02

    if helpful:
        weights["urgency_weight"] += delta
        weights["importance_weight"] += delta
    else:
        weights["urgency_weight"] = max(0.1, weights["urgency_weight"] - delta)
        weights["importance_weight"] = max(0.1, weights["importance_weight"] - delta)

    save_user_weights(weights)

    return Response({
        "message": "Feedback applied",
        "weights": weights,
        "helpful": helpful,
        "selected": selected,
    })
