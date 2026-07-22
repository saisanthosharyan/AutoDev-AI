import asyncio

from app.agents.fixer import FixerAgent
from app.builders.project_builder import ProjectBuilder
from app.core.logger import logger

from app.services.execution.execution_manager import ExecutionManager
from app.services.debugger.debug_manager import DebugManager


class RetryManager:
    """
    Executes a generated project and automatically repairs it
    if execution fails.
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
        Returns

        execution_result
        updated_project
        updated_code
        debug_report
        """

        execution_result = None
        debug_report = ""

        for attempt in range(1, self.max_retries + 1):

            logger.info("=" * 60)
            logger.info(
                f"Execution Attempt {attempt}/{self.max_retries}"
            )
            logger.info("=" * 60)

            # ------------------------------------------
            # Execute Project
            # ------------------------------------------

            try:

                execution_result = self.executor.run(
                    project["project_path"]
                )

            except Exception as e:

                logger.exception(
                    "Execution crashed."
                )

                execution_result = {
                    "success": False,
                    "stdout": "",
                    "stderr": str(e),
                    "return_code": -1,
                    "execution_time": 0,
                }

            # ------------------------------------------
            # Success
            # ------------------------------------------

            if execution_result.get("success"):

                logger.info(
                    "Project executed successfully."
                )

                return (
                    execution_result,
                    project,
                    code,
                    debug_report,
                )

            logger.warning(
                "Execution failed."
            )

            # ------------------------------------------
            # Analyze Failure
            # ------------------------------------------

            debug_report = self.debugger.analyze(
                execution_result
            )

            logger.info(
                "Debug analysis completed."
            )

            # ------------------------------------------
            # AI Repair
            # ------------------------------------------

            try:

                logger.info(
                    "Requesting AI to repair project..."
                )

                fixed_code = await self.fixer.run(
                    code=code,
                    review=review,
                    execution_error=debug_report,
                )

                if not fixed_code.strip():

                    logger.error(
                        "Fixer returned empty response."
                    )

                    break

                if fixed_code == code:

                    logger.warning(
                        "Fixer produced identical code."
                    )

                else:

                    logger.info(
                        "Fixer generated improved code."
                    )

                code = fixed_code

            except Exception:

                logger.exception(
                    "Automatic repair failed."
                )

                break

            # ------------------------------------------
            # Rebuild Project
            # ------------------------------------------

            try:

                logger.info(
                    "Rebuilding project..."
                )

                project = self.builder.rebuild(
                    project["project_path"],
                    code,
                )

                logger.info(
                    "Project rebuilt successfully."
                )

            except Exception:

                logger.exception(
                    "Project rebuild failed."
                )

                break

            # ------------------------------------------
            # Small Delay
            # ------------------------------------------

            await asyncio.sleep(1)

        logger.error(
            "Maximum retry limit reached."
        )

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