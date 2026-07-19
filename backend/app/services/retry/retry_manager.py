from app.agents.fixer import FixerAgent
from app.builders.project_builder import ProjectBuilder
from app.core.logger import logger

from app.services.execution.execution_manager import ExecutionManager
from app.services.debugger.debug_manager import DebugManager


class RetryManager:
    """
    Handles automatic project repair and retry execution.
    """

    def __init__(self, max_retries: int = 3):
        self.max_retries = max_retries

        self.executor = ExecutionManager()
        self.debugger = DebugManager()
        self.builder = ProjectBuilder()
        self.fixer = FixerAgent()

    async def execute_with_retry(
        self,
        project: dict,
        code: str,
        review: str = "",
    ):
        """
        Execute a generated project.

        If execution fails:
            • analyze errors
            • repair project
            • rebuild project
            • retry execution

        Returns:
            execution_result,
            updated_project,
            updated_code,
            debug_report
        """

        execution_result = None
        debug_report = ""

        for attempt in range(1, self.max_retries + 1):

            logger.info(
                f"Execution Attempt {attempt}/{self.max_retries}"
            )

            try:

                execution_result = self.executor.run(
                    project["project_path"]
                )

            except Exception as e:

                logger.exception("Execution crashed.")

                execution_result = {
                    "success": False,
                    "stdout": "",
                    "stderr": str(e),
                    "return_code": -1,
                    "execution_time": 0,
                }

            if execution_result.get("success"):

                logger.info("Execution successful.")

                return (
                    execution_result,
                    project,
                    code,
                    "",
                )

            logger.warning("Execution failed.")

            debug_report = self.debugger.analyze(
                execution_result
            )

            try:

                fixed_code = await self.fixer.run(
                    code=code,
                    review=review,
                    execution_error=debug_report,
                )

                code = fixed_code

                project = self.builder.rebuild(
                    project["project_path"],
                    code,
                )

            except Exception:

                logger.exception(
                    "Automatic repair failed."
                )

                break

        if execution_result is None:

            execution_result = {
                "success": False,
                "stdout": "",
                "stderr": "Execution never started.",
                "return_code": -1,
                "execution_time": 0,
            }

        return (
            execution_result,
            project,
            code,
            debug_report,
        )