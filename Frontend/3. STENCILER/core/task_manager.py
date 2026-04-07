import uuid
from typing import Dict, Any, Optional
from datetime import datetime

class TaskStatus:
    def __init__(self, task_id: str):
        self.task_id = task_id
        self.step = "pending"
        self.comment = "Initialisation..."
        self.success = None
        self.data = None
        self.error = None
        self.created_at = datetime.now()
        self.updated_at = datetime.now()

    def update(self, step: str, comment: str, success: Optional[bool] = None, data: Any = None, error: str = None):
        self.step = step
        self.comment = comment
        if success is not None:
            self.success = success
        if data is not None:
            self.data = data
        if error is not None:
            self.error = error
        self.updated_at = datetime.now()

    def to_dict(self):
        return {
            "task_id": self.task_id,
            "step": self.step,
            "comment": self.comment,
            "success": self.success,
            "data": self.data,
            "error": self.error,
            "updated_at": self.updated_at.isoformat()
        }

class TaskManager:
    _tasks: Dict[str, TaskStatus] = {}

    @classmethod
    def create_task(cls) -> TaskStatus:
        task_id = str(uuid.uuid4())
        status = TaskStatus(task_id)
        cls._tasks[task_id] = status
        return status

    @classmethod
    def get_task(cls, task_id: str) -> Optional[TaskStatus]:
        return cls._tasks.get(task_id)

    @classmethod
    def cleanup_old_tasks(cls, max_age_seconds: int = 3600):
        # Optional: cleanup logic
        pass

task_manager = TaskManager()
