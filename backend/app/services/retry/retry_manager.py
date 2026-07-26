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
    when execution fails.

    Flow:

        Execute
           ↓
        Debug
           ↓
        Fixer Agent
           ↓
        Rebuild
           ↓
        Execute Again
           ↓
        Success / Retry
    """

    def __init__(
        self,
        max_retries: int = 3,
    ):

        self.max_retries = max(
            1,
            max_retries,
        )

        self.executor = ExecutionManager()

        self.debugger = DebugManager()

        self.builder = ProjectBuilder()

        self.fixer = FixerAgent()

    # ==========================================================
    # MAIN EXECUTION LOOP
    # ==========================================================

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

        if not project:

            raise ValueError(
                "Project information cannot be empty."
            )

        if not project.get(
            "project_path"
        ):

            raise ValueError(
                "Project path is missing."
            )

        if not code or not code.strip():

            raise ValueError(
                "Generated project code cannot be empty."
            )

        execution_result = None

        debug_report = {}

        current_project = project

        current_code = code

        # ======================================================
        # RETRY LOOP
        # ======================================================

        for attempt in range(
            1,
            self.max_retries + 1,
        ):

            logger.info("=" * 60)

            logger.info(
                f"Execution Attempt "
                f"{attempt}/{self.max_retries}"
            )

            logger.info("=" * 60)

            # ==================================================
            # EXECUTE
            # ==================================================

            try:

                execution_result = (
                    self.executor.run(
                        current_project[
                            "project_path"
                        ]
                    )
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

            if execution_result.get(
                "success",
                False,
            ):

                logger.info(
                    f"Project executed successfully "
                    f"on attempt {attempt}."
                )

                return (
                    execution_result,
                    current_project,
                    current_code,
                    debug_report,
                )

            # ==================================================
            # FAILURE
            # ==================================================

            logger.warning(
                f"Execution failed on attempt {attempt}."
            )

            stderr = execution_result.get(
                "stderr",
                "",
            )

            if stderr:

                logger.error(
                    stderr
                )

            # ==================================================
            # DEBUG
            # ==================================================

            try:

                debug_report = (
                    self.debugger.analyze(
                        execution_result
                    )
                )

                logger.info(
                    "Debug analysis completed."
                )

            except Exception as e:

                logger.exception(
                    "Debug analysis failed."
                )

                debug_report = {
                    "error": str(e),
                    "root_cause": (
                        "Debug analysis failed."
                    ),
                    "solution": (
                        "Inspect execution logs manually."
                    ),
                    "category": "DebugError",
                    "summary": (
                        "Debug analysis failed."
                    ),
                    "recommendation": (
                        "Inspect stdout and stderr."
                    ),
                    "stdout": execution_result.get(
                        "stdout",
                        "",
                    ),
                    "stderr": execution_result.get(
                        "stderr",
                        "",
                    ),
                    "return_code": execution_result.get(
                        "return_code",
                        -1,
                    ),
                }

            # ==================================================
            # LAST ATTEMPT
            # ==================================================

            if attempt >= self.max_retries:

                logger.error(
                    "No repair attempt remaining."
                )

                break

            # ==================================================
            # AI REPAIR
            # ==================================================

            try:

                logger.info(
                    "Requesting AI to repair project..."
                )

                old_code = current_code

                fixed_code = await self.fixer.run(
                    code=current_code,
                    review=review,
                    execution_error=debug_report,
                )

                # ------------------------------------------------
                # Validate response
                # ------------------------------------------------

                if not fixed_code:

                    logger.error(
                        "Fixer returned empty response."
                    )

                    break

                fixed_code = fixed_code.strip()

                if not fixed_code:

                    logger.error(
                        "Fixer returned empty code."
                    )

                    break

                # ------------------------------------------------
                # Check whether AI actually changed anything
                # ------------------------------------------------

                if fixed_code == old_code:

                    logger.warning(
                        "Fixer returned code identical "
                        "to the previous version."
                    )

                    break

                logger.info(
                    f"Old code size: "
                    f"{len(old_code)} chars"
                )

                logger.info(
                    f"New code size: "
                    f"{len(fixed_code)} chars"
                )

                # =================================================
                # REBUILD
                # =================================================

                logger.info(
                    "Rebuilding repaired project..."
                )

                updated_project = (
                    self.builder.rebuild(
                        current_project[
                            "project_path"
                        ],
                        fixed_code,
                    )
                )

                current_project = (
                    updated_project
                )

                current_code = (
                    fixed_code
                )

                logger.info(
                    "Project rebuilt successfully."
                )

                # =================================================
                # SAVE REPAIR REPORT
                # =================================================

                try:

                    reporter = RepairReporter(
                        current_project[
                            "project_path"
                        ]
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

                # =================================================
                # Small delay
                # =================================================

                await asyncio.sleep(
                    1
                )

            except Exception as e:

                logger.exception(
                    "Automatic repair failed."
                )

                debug_report = {
                    **(
                        debug_report
                        if isinstance(
                            debug_report,
                            dict,
                        )
                        else {}
                    ),

                    "repair_error": str(e),
                }

                break

        # ======================================================
        # FAILED AFTER RETRIES
        # ======================================================

        logger.error(
            f"Project failed after "
            f"{self.max_retries} execution attempts."
        )

        if execution_result is None:

            execution_result = {
                "success": False,
                "stdout": "",
                "stderr": (
                    "Execution never started."
                ),
                "return_code": -1,
                "execution_time": 0,
            }

        return (
            execution_result,
            current_project,
            current_code,
            debug_report,
        )