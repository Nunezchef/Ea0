from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4


LEARNING_TASK_NAME = "ea0-learning-v1"


def _build_prompt(workspace_root: Path) -> str:
    return (
        "Process pending EA0 learning observations for this Agent0 instance. "
        "Use the `ea0_learning_tool` to process observations with "
        f"`workspace_root={workspace_root}` and then stop."
    )


def _tasks_file(workspace_root: Path) -> Path:
    return workspace_root / "usr/scheduler/tasks.json"


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _build_fallback_task(*, workspace_root: Path) -> dict[str, object]:
    task_uuid = uuid4().hex[:8]
    timestamp = _utc_now()
    return {
        "uuid": task_uuid,
        "name": LEARNING_TASK_NAME,
        "state": "idle",
        "system_prompt": "You are running a background EA0 continuous-learning maintenance task.",
        "prompt": _build_prompt(workspace_root),
        "attachments": [],
        "project_name": None,
        "project_color": None,
        "created_at": timestamp,
        "updated_at": timestamp,
        "last_run": None,
        "next_run": None,
        "last_result": None,
        "context_id": task_uuid,
        "dedicated_context": True,
        "project": {
            "name": None,
            "color": None,
        },
        "type": "scheduled",
        "schedule": {
            "minute": "*/15",
            "hour": "*",
            "day": "*",
            "month": "*",
            "weekday": "*",
            "timezone": "UTC",
        },
    }


def _ensure_learning_schedule_fallback(*, workspace_root: Path) -> dict[str, str]:
    tasks_file = _tasks_file(workspace_root)
    tasks_file.parent.mkdir(parents=True, exist_ok=True)

    payload: dict[str, list[dict[str, object]]]
    if tasks_file.exists():
        try:
            payload = json.loads(tasks_file.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            payload = {"tasks": []}
    else:
        payload = {"tasks": []}

    tasks = payload.get("tasks")
    if not isinstance(tasks, list):
        tasks = []
        payload["tasks"] = tasks

    for task in tasks:
        if isinstance(task, dict) and task.get("name") == LEARNING_TASK_NAME:
            return {
                "status": "exists",
                "name": LEARNING_TASK_NAME,
                "uuid": str(task.get("uuid", "")),
            }

    task = _build_fallback_task(workspace_root=workspace_root)
    tasks.append(task)
    tasks_file.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return {
        "status": "created",
        "name": LEARNING_TASK_NAME,
        "uuid": str(task["uuid"]),
    }


async def ensure_learning_schedule(*, workspace_root: Path) -> dict[str, str]:
    try:
        from python.helpers.task_scheduler import TaskScheduler, ScheduledTask, TaskSchedule
    except ModuleNotFoundError as e:
        result = _ensure_learning_schedule_fallback(workspace_root=workspace_root)
        result["warning"] = str(e)
        return result

    scheduler = TaskScheduler.get()
    existing = scheduler.get_task_by_name(LEARNING_TASK_NAME)
    if existing:
        return {
            "status": "exists",
            "name": LEARNING_TASK_NAME,
            "uuid": existing.uuid,
        }

    schedule = TaskSchedule(minute="*/15", hour="*", day="*", month="*", weekday="*")
    task = ScheduledTask.create(
        name=LEARNING_TASK_NAME,
        system_prompt="You are running a background EA0 continuous-learning maintenance task.",
        prompt=_build_prompt(workspace_root),
        schedule=schedule,
        attachments=[],
        context_id=None,
    )
    await scheduler.add_task(task)
    await scheduler.save()
    return {
        "status": "created",
        "name": LEARNING_TASK_NAME,
        "uuid": task.uuid,
    }
