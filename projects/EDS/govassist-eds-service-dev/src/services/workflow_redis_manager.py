from src.core.config import configs


class WorkflowRedisSchema:
    """Redis schema manager for workflow data"""

    def __init__(self, app_name: str = "sharepoint", environment: str = configs.ENV):
        self.app = app_name.lower()
        self.env = environment.lower()
        self.separator = ":"

    def _build_key(self, *parts: str) -> str:
        """Build Redis key with consistent naming"""
        clean_parts = [str(part).lower().replace(" ", "_") for part in parts if part]
        return f"{self.app}{self.separator}{self.env}{self.separator}{self.separator.join(clean_parts)}"

    # Workflow state keys
    def workflow_state_key(self, workflow_id: str) -> str:
        """Main workflow state storage"""
        return self._build_key("workflow", "state", workflow_id)

    def workflow_logs_key(self, workflow_id: str) -> str:
        """Workflow logs (list)"""
        return self._build_key("workflow", "logs", workflow_id)

    def workflow_files_key(self, workflow_id: str) -> str:
        """Individual file processing states (hash)"""
        return self._build_key("workflow", "files", workflow_id)

    # Cache keys
    def folder_last_processing_key(
        self, drive_id: str, folder_id: str, folder_type: str
    ) -> str:
        """Last processing info for folder"""
        return self._build_key(
            "cache", "last_processing", folder_type, f"{drive_id}_{folder_id}"
        )

    def workflow_result_key(self, workflow_id: str) -> str:
        """Workflow result"""
        return self._build_key("workflow", "result", workflow_id)

    def workflow_status_key(self, folder_id: str) -> str:
        """Workflow status"""
        return self._build_key("workflow", "status", folder_id)
