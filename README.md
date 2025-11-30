# Smart Task Analyzer

## Overview
Mini-application that scores and prioritizes tasks using urgency, importance, effort, and dependencies. Backend: Django + DRF. Frontend: simple HTML/CSS/JS that consumes API.



## Project structure
(see file tree in repository)

## Setup (local)
1. Ensure Python 3.8+ installed.
2. Create virtualenv:
3. Install dependencies:
4. Run migrations:
(No models required — but migration creates DB)
5. Start Django development server:
6. Open frontend:
- Serve `frontend/` files. For quick local testing, open `backend/task_analyzer/urls.py` to add static serving or just open `frontend/index.html` in the browser and set `API_BASE` to `http://127.0.0.1:3000/api/tasks/` in `script.js`.
- For convenience, you can copy `frontend/` into a simple static server dir.

## API Endpoints
- `POST /api/tasks/analyze/`
- Body: `{ "tasks": [ ... ], "weights": {urgency:..,..} , "strategy": "smart|fastest|impact|deadline" }`
- Returns: sorted tasks with `score` and `reason`. Includes `cycles` if circular dependencies detected.

- `GET /api/tasks/suggest/?tasks=<json>&strategy=...`
- Returns top 3 suggestions for today with explanations.

## Algorithm Explanation (300-500 words)
The scoring algorithm calculates a normalized priority score by combining four components: urgency, importance, effort, and dependencies. Urgency is derived from how close the due date is; tasks past their due date receive a large urgency boost to ensure they surface quickly. Importance uses the user-specified 1–10 scale. Effort favors low estimated_hours, treating quick tasks as "quick wins" (effort component uses the inverse of estimated hours). Dependencies are scored by counting how many other tasks depend on a given task — tasks blocking many others receive a higher dependency score.

To combine these heterogeneous measures, each component is normalized across the task batch (min-max normalization) to a 0–1 range. The normalized components are weighted and summed. Default weights are: urgency 0.35, importance 0.35, effort 0.15, dependencies 0.15. The system supports preset strategies (Fastest Wins, High Impact, Deadline Driven, Smart Balance) that overwrite weights to match each strategy’s intent. We also accept custom weights in API requests.

Edge cases: no due date tasks are treated with neutral urgency. Past-due tasks receive a ramped urgency so the older the overdue, the higher the urgency. Invalid or missing fields are validated, with defaults (importance=5, estimated_hours=1). Circular dependencies are detected using DFS; when found the API reports cycles to the client and includes the cycles in the response for user correction.

Trade-offs: Min-max normalization makes scores relative to the current batch (meaning absolute score values vary by batch). This design helps prioritize within the current task set; for global/long-term ranking one could add historical scaling. Another trade-off is using a simple count of dependents rather than a full centrality metric — count is simpler and faster, and suits the assignment scope. Future improvements include date intelligence (skip weekends/holidays), a learning system to adjust weights from user feedback, and a graph visualization for dependencies.

## Tests
Run tests with:

## Time breakdown
- Algorithm & scoring core: ~1.5 hours
- Backend endpoints & validation: ~1 hour
- Frontend UI & interactions: ~1 hour
- Tests & README: ~0.5 hour

## Future Improvements
- Persist tasks in DB with user sessions
- Dependency graph visualization and auto-fix suggestions
- Consider business days only for urgency
- Machine learning to adapt weights from user feedback

