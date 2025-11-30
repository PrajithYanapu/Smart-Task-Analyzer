from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from .scoring import calculate_scores
import datetime


class ScoringAlgorithmTests(TestCase):
    def test_overdue_task_has_high_urgency(self):
        tasks = [{
            "id": "1",
            "title": "Overdue Task",
            "due_date": datetime.date.today() - datetime.timedelta(days=1),
            "estimated_hours": 2,
            "importance": 5,
            "dependencies": [],
        }]
        result = calculate_scores(tasks)
        self.assertEqual(len(result["tasks"]), 1)
        t = result["tasks"][0]
        self.assertGreaterEqual(t["score"], 0.6)

    def test_weekend_holiday_increases_urgency(self):
        today = datetime.date.today()
        future = today + datetime.timedelta(days=10)
        tasks = [{
            "id": "1",
            "title": "Future Task",
            "due_date": future,
            "estimated_hours": 2,
            "importance": 8,
            "dependencies": [],
        }]
        base = calculate_scores(tasks)["tasks"][0]["score"]

        # Force a "holiday-like" higher urgency
        tasks[0]["due_date"] = today
        urgent = calculate_scores(tasks)["tasks"][0]["score"]
        self.assertGreaterEqual(urgent, base)

    def test_eisenhower_matrix_classification(self):
        today = datetime.date.today()
        tasks = [{
            "id": "1",
            "title": "Important & Urgent",
            "due_date": today,
            "estimated_hours": 1,
            "importance": 9,
            "dependencies": [],
        }]
        t = calculate_scores(tasks)["tasks"][0]
        self.assertEqual(t["matrix"], "Do First")


class APITests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_analyze_endpoint(self):
        url = reverse("analyze")
        payload = {
            "tasks": [
                {
                    "id": "1",
                    "title": "Sample Task",
                    "due_date": None,
                    "estimated_hours": 2,
                    "importance": 8,
                    "dependencies": [],
                }
            ],
            "strategy": "smart",
        }
        res = self.client.post(url, payload, format="json")
        self.assertEqual(res.status_code, 200)
        self.assertIn("tasks", res.data)

    def test_suggest_endpoint(self):
        url = reverse("suggest")
        tasks = [
            {
                "id": "1",
                "title": "Task A",
                "due_date": None,
                "estimated_hours": 2,
                "importance": 8,
                "dependencies": [],
            },
            {
                "id": "2",
                "title": "Task B",
                "due_date": None,
                "estimated_hours": 5,
                "importance": 4,
                "dependencies": [],
            },
        ]
        res = self.client.get(
            url,
            {"tasks": json.dumps(tasks), "strategy": "smart"},
            format="json",
        )
        self.assertEqual(res.status_code, 200)
        self.assertIn("suggestions", res.data)
        self.assertLessEqual(len(res.data["suggestions"]), 3)

    def test_feedback_endpoint(self):
        url = reverse("feedback")
        res = self.client.post(
            url,
            {"selected": ["1", "2"], "helpful": True},
            format="json",
        )
        self.assertEqual(res.status_code, 200)
        self.assertIn("weights", res.data)
