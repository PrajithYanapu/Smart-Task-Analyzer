import datetime
import json
import os
from collections import defaultdict, deque

# --------------------------------------------------------------------
# Weights file for learning system
# --------------------------------------------------------------------
WEIGHTS_FILE = os.path.join(os.path.dirname(__file__), "user_weights.json")


def load_user_weights():
    """Load user-tuned weights, or fall back to defaults."""
    if os.path.exists(WEIGHTS_FILE):
        try:
            with open(WEIGHTS_FILE, "r") as f:
                data = json.load(f)
                return {
                    "urgency_weight": float(data.get("urgency_weight", 1.0)),
                    "importance_weight": float(data.get("importance_weight", 1.0)),
                    "effort_weight": float(data.get("effort_weight", 1.0)),
                }
        except Exception:
            pass
    return {
        "urgency_weight": 1.0,
        "importance_weight": 1.0,
        "effort_weight": 1.0,
    }


# --------------------------------------------------------------------
# Date intelligence: weekends + holidays
# --------------------------------------------------------------------
HOLIDAYS = {
    # Example fixed holidays – adjust to your country as needed
    "2025-01-01",  # New Year
    "2025-01-26",  # Republic Day (India)
    "2025-08-15",  # Independence Day
    "2025-10-02",  # Gandhi Jayanti
    "2025-12-25",  # Christmas
}


def is_weekend(d: datetime.date) -> bool:
    return d.weekday() >= 5  # Saturday (5), Sunday (6)


def is_holiday(d: datetime.date) -> bool:
    return d.strftime("%Y-%m-%d") in HOLIDAYS


def business_days_between(start: datetime.date, end: datetime.date) -> int:
    """
    Count *working* days between start and end (exclusive of start, inclusive of end).
    Weekends and holidays are skipped.
    """
    if end <= start:
        return 0
    days = 0
    current = start + datetime.timedelta(days=1)
    while current <= end:
        if not is_weekend(current) and not is_holiday(current):
            days += 1
        current += datetime.timedelta(days=1)
    return days


# --------------------------------------------------------------------
# Eisenhower Matrix
# --------------------------------------------------------------------
def eisenhower_category(importance: int, urgency_score: float) -> str:
    """
    Classify into Eisenhower quadrant.
    importance: 1–10
    urgency_score: 0–1
    """
    important = importance >= 6
    urgent = urgency_score >= 0.6

    if important and urgent:
        return "Do First"
    if important and not urgent:
        return "Schedule"
    if not important and urgent:
        return "Delegate"
    return "Eliminate"


# --------------------------------------------------------------------
# Cycle detection in dependency graph
# --------------------------------------------------------------------
def detect_cycles(task_list):
    """
    Detects cycles in dependency graph using DFS.
    Returns list of cycles, each cycle is list of ids.
    """
    graph = defaultdict(list)
    for t in task_list:
        tid = t["id"]
        for dep in t.get("dependencies", []):
            graph[dep].append(tid)

    visited = set()
    stack = set()
    cycles = []

    def dfs(node, path):
        if node in stack:
            # Found a cycle – take slice from first occurrence of node
            if node in path:
                idx = path.index(node)
                cycles.append(path[idx:] + [node])
            return
        if node in visited:
            return

        visited.add(node)
        stack.add(node)
        for nei in graph.get(node, []):
            dfs(nei, path + [nei])
        stack.remove(node)

    for t in task_list:
        tid = t["id"]
        if tid not in visited:
            dfs(tid, [tid])

    # Deduplicate simple cycles
    unique = []
    seen = set()
    for c in cycles:
        key = tuple(c)
        if key not in seen:
            seen.add(key)
            unique.append(c)
    return unique


# --------------------------------------------------------------------
# Main scoring function
# --------------------------------------------------------------------
def calculate_scores(tasks, weights=None, strategy=None):
    """
    tasks: list of validated serializer data (dicts)
    weights: optional override, else load from user_weights.json
    strategy: "fastest" | "impact" | "deadline" | "smart" or None
    returns: {"tasks": [...], "cycles": [...]}
    """
    # Use learned weights if not provided explicitly
    base_weights = weights or load_user_weights()

    uw = base_weights.get("urgency_weight", 1.0)
    iw = base_weights.get("importance_weight", 1.0)
    ew = base_weights.get("effort_weight", 1.0)

    # Apply strategy bias on top of learned weights
    if strategy == "fastest":
        ew *= 1.5
    elif strategy == "impact":
        iw *= 1.5
    elif strategy == "deadline":
        uw *= 1.5
    # "smart" or None → keep as-is

    now = datetime.date.today()

    scored = []
    for t in tasks:
        tid = t["id"]
        title = t["title"]
        due_date = t.get("due_date")  # already a date or None (from serializer)
        est_hours = float(t.get("estimated_hours") or 1.0)
        importance = int(t.get("importance") or 5)
        deps = t.get("dependencies") or []

        # ----- Urgency with date intelligence -----
        if due_date:
            # assume serializer converted to date; if string, guard:
            if isinstance(due_date, str):
                due_date = datetime.date.fromisoformat(due_date)
            if due_date < now:
                # overdue
                days_left = 0
                overdue = True
            else:
                days_left = business_days_between(now, due_date)
                overdue = False

            # basic urgency: closer deadline → higher urgency
            # 0 days → 1.0, 10 days → 0.0 approx (clamped)
            urgency_score = max(0.0, min(1.0, 1.0 - (days_left / 10.0)))

            # weekend / holiday adjustments
            if is_weekend(due_date):
                urgency_score += 0.1  # weekend deadlines are trickier
            if is_holiday(due_date):
                urgency_score += 0.15  # holidays matter more

            if overdue:
                urgency_score = 1.0  # fully urgent if already past due
        else:
            urgency_score = 0.2  # no deadline → mild urgency

        urgency_score = max(0.0, min(1.0, urgency_score))

        # ----- Importance (normalize 1–10 → 0–1) -----
        importance_score = max(1, min(10, importance)) / 10.0

        # ----- Effort: quick wins priority (smaller hours → higher score) -----
        # Cap at 12h; more than that is treated as "heavy"
        capped = min(est_hours, 12.0)
        effort_score = 1.0 - (capped / 12.0)  # 1h ~0.92, 12h ~0.0

        # ----- Final score with weights -----
        score = (
            uw * urgency_score +
            iw * importance_score +
            ew * effort_score
        )

        # Normalize roughly into 0–1
        # (weights may increase above 1, so divide by sum of weights)
        denom = uw + iw + ew if (uw + iw + ew) > 0 else 1.0
        score = score / denom
        score = round(score, 3)

        # Eisenhower category
        matrix = eisenhower_category(importance, urgency_score)

        # Reason string (short explanation)
        reason_parts = []
        reason_parts.append(f"Urgency: {round(urgency_score,2)}")
        reason_parts.append(f"Importance: {importance}")
        reason_parts.append(f"Effort: {est_hours}h (quick-win={round(effort_score,2)})")
        reason_parts.append(f"Matrix: {matrix}")
        if deps:
            reason_parts.append(f"Depends on: {', '.join(deps)}")
        reason = " | ".join(reason_parts)

        scored.append({
            "id": tid,
            "title": title,
            "due_date": due_date.isoformat() if isinstance(due_date, datetime.date) else due_date,
            "estimated_hours": est_hours,
            "importance": importance,
            "dependencies": deps,
            "score": score,
            "reason": reason,
            "matrix": matrix,
        })

    # Detect cycles
    cycles = detect_cycles(scored)

    # Sort descending by score
    scored.sort(key=lambda x: x["score"], reverse=True)

    return {
        "tasks": scored,
        "cycles": cycles,
    }
