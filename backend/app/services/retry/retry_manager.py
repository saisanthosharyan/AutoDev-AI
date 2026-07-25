import asyncio

from app.agents.fixer import FixerAgent
from app.builders.project_builder import ProjectBuilder
from app.core.logger import logger

from app.services.execution.execution_manager import ExecutionManager
from app.services.debugger.debug_manager import DebugManager
from app.services.repair.repair_report import RepairReporter


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
        Returns:

        execution_result
        updated_project
        updated_code
        debug_report
        """

        execution_result = None
        debug_report = ""

        for attempt in range(
            1,
            self.max_retries + 1,
        ):

            logger.info("=" * 60)
            logger.info(
                f"Execution Attempt {attempt}/{self.max_retries}"
            )
            logger.info("=" * 60)

            # ==================================================
            # EXECUTE
            # ==================================================

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

            # ==================================================
            # SUCCESS
            # ==================================================

            if execution_result.get("success"):

                logger.info(
                    f"Project executed successfully on attempt {attempt}."
                )

                return (
                    execution_result,
                    project,
                    code,
                    debug_report,
                )

            # ==================================================
            # EXECUTION FAILED
            # ==================================================

            logger.warning(
                "Execution failed."
            )

            logger.error(
                execution_result.get(
                    "stderr",
                    "Unknown execution error.",
                )
            )

            # ==================================================
            # DEBUG
            # ==================================================

            try:

                debug_report = self.debugger.analyze(
                    execution_result
                )

                logger.info(
                    "Debug analysis completed."
                )

            except Exception as e:

                logger.exception(
                    "Debug analysis failed."
                )

                debug_report = (
                    f"Debug analysis failed: {str(e)}"
                )

            # ==================================================
            # AI REPAIR
            # ==================================================

            try:

                logger.info(
                    "Requesting AI to repair project..."
                )

                old_code = code

                fixed_code = await self.fixer.run(
                    code=code,
                    review=review,
                    execution_error=debug_report,
                )

                if not fixed_code:

                    logger.error(
                        "Fixer returned empty response."
                    )

                    break

                fixed_code = fixed_code.strip()

                if not fixed_code:

                    logger.error(
                        "Fixer returned empty code after stripping."
                    )

                    break

                if fixed_code == old_code:

                    logger.warning(
                        "Fixer produced identical code."
                    )

                else:

                    logger.info(
                        f"Old code size: {len(old_code)} chars"
                    )

                    logger.info(
                        f"New code size: {len(fixed_code)} chars"
                    )

                code = fixed_code

                # ==================================================
                # SAVE REPAIR REPORT
                # ==================================================

                try:

                    reporter = RepairReporter(
                        project["project_path"]
                    )

                    reporter.save(
                        old_code=old_code,
                        new_code=fixed_code,
                        debug_report=debug_report,
                    )

                    logger.info(
                        "Repair report saved successfully."
                    )

                except Exception:

                    logger.exception(
                        "Failed to save repair report."
                    )

            except Exception:

                logger.exception(
                    "Automatic repair failed."
                )

                break

            # ==================================================
            # REBUILD
            # ==================================================

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

            # ==================================================
            # SMALL DELAY
            # ==================================================

            await asyncio.sleep(1)

        # ==================================================
        # MAX RETRIES
        # ==================================================

        logger.error(
            f"Maximum retry limit ({self.max_retries}) reached."
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