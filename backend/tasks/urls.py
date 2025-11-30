from django.urls import path
from .views import (
    AnalyzeTasksView,
    suggest_tasks,
    task_graph,       # NEW
    feedback,         # NEW
)

urlpatterns = [
    path('analyze/', AnalyzeTasksView.as_view(), name='analyze'),
    path('suggest/', suggest_tasks, name='suggest'),

    # NEW BONUS ENDPOINTS
    path('graph/', task_graph, name='graph'),
    path('feedback/', feedback, name='feedback'),
]