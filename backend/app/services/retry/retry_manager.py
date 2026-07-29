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

    The retry manager does NOT create separate test projects.
    It works on the existing generated project.
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
        review=None,
    ):
        """
        Execute a generated project and automatically repair it
        when execution fails.

        Returns:

            execution_result
            updated_project
            updated_code
            debug_report
        """

        # ------------------------------------------------------
        # Validate input
        # ------------------------------------------------------

        if not project:
            raise ValueError(
                "Project information cannot be empty."
            )

        project_path = project.get(
            "project_path"
        )

        if not project_path:
            raise ValueError(
                "Project path is missing."
            )

        if not code or not code.strip():
            raise ValueError(
                "Generated project code cannot be empty."
            )

        # ------------------------------------------------------
        # Current state
        # ------------------------------------------------------

        current_project = project
        current_code = code

        execution_result = None
        debug_report = {}

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
            # STEP 1 - EXECUTE
            # ==================================================

            try:
                execution_result = self.executor.run(
                    current_project["project_path"]
                )

            except Exception as exc:

                logger.exception(
                    "Execution crashed."
                )

                execution_result = {
                    "success": False,
                    "stdout": "",
                    "stderr": str(exc),
                    "return_code": -1,
                    "execution_time": 0,
                }

            # --------------------------------------------------
            # Normalize execution result
            # --------------------------------------------------

            if not isinstance(
                execution_result,
                dict,
            ):
                execution_result = {
                    "success": False,
                    "stdout": "",
                    "stderr": (
                        "ExecutionManager returned "
                        "an invalid result."
                    ),
                    "return_code": -1,
                    "execution_time": 0,
                }

            # ==================================================
            # STEP 2 - SUCCESS
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
            # STEP 3 - EXECUTION FAILED
            # ==================================================

            logger.warning(
                f"Execution failed on attempt {attempt}."
            )

            stderr = execution_result.get(
                "stderr",
                "",
            )

            stdout = execution_result.get(
                "stdout",
                "",
            )

            if stderr:
                logger.error(
                    f"STDERR:\n{stderr}"
                )

            if stdout:
                logger.info(
                    f"STDOUT:\n{stdout}"
                )

            # ==================================================
            # STEP 4 - DEBUG
            # ==================================================

            try:

                debug_report = self.debugger.analyze(
                    execution_result
                )

                if not isinstance(
                    debug_report,
                    dict,
                ):
                    debug_report = {
                        "summary": str(
                            debug_report
                        ),
                        "stdout": stdout,
                        "stderr": stderr,
                        "return_code": execution_result.get(
                            "return_code",
                            -1,
                        ),
                    }

                logger.info(
                    "Debug analysis completed."
                )

            except Exception as exc:

                logger.exception(
                    "Debug analysis failed."
                )

                debug_report = {
                    "error": str(exc),
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
                    "stdout": stdout,
                    "stderr": stderr,
                    "return_code": execution_result.get(
                        "return_code",
                        -1,
                    ),
                }

            # ==================================================
            # STEP 5 - NO RETRIES LEFT
            # ==================================================

            if attempt >= self.max_retries:

                logger.error(
                    "Maximum retry attempts reached."
                )

                break

            # ==================================================
            # STEP 6 - AI REPAIR
            # ==================================================

            logger.info(
                "Requesting AI to repair project..."
            )

            old_code = current_code

            try:

                fixed_code = await self.fixer.run(
                    code=current_code,
                    review=review,
                    execution_error=debug_report,
                )

            except Exception as exc:

                logger.exception(
                    "Fixer Agent failed."
                )

                debug_report = {
                    **debug_report,
                    "repair_error": str(exc),
                }

                break

            # --------------------------------------------------
            # Validate fixer response
            # --------------------------------------------------

            if not fixed_code:

                logger.error(
                    "Fixer Agent returned empty response."
                )

                break

            fixed_code = fixed_code.strip()

            if not fixed_code:

                logger.error(
                    "Fixer Agent returned empty response."
                )

                break

            # --------------------------------------------------
            # Check whether anything changed
            # --------------------------------------------------

            if fixed_code == old_code:

                logger.warning(
                    "Fixer Agent returned code identical "
                    "to the previous version."
                )

                debug_report = {
                    **debug_report,
                    "repair_error": (
                        "Fixer returned unchanged code."
                    ),
                }

                break

            logger.info(
                f"Old code size: {len(old_code)} characters"
            )

            logger.info(
                f"New code size: {len(fixed_code)} characters"
            )

            # ==================================================
            # STEP 7 - REBUILD
            # ==================================================

            try:

                logger.info(
                    "Rebuilding repaired project..."
                )

                updated_project = self.builder.rebuild(
                    current_project["project_path"],
                    fixed_code,
                )

                if not updated_project:
                    raise RuntimeError(
                        "ProjectBuilder returned no project."
                    )

                if not updated_project.get(
                    "project_path"
                ):
                    raise RuntimeError(
                        "Rebuilt project path is missing."
                    )

                current_project = updated_project
                current_code = fixed_code

                logger.info(
                    "Repaired project rebuilt successfully."
                )

            except Exception as exc:

                logger.exception(
                    "Project rebuild failed."
                )

                debug_report = {
                    **debug_report,
                    "repair_error": str(exc),
                }

                break

            # ==================================================
            # STEP 8 - SAVE REPAIR REPORT
            # ==================================================

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

            # --------------------------------------------------
            # Next iteration executes repaired project
            # --------------------------------------------------

            logger.info(
                "Repaired project will now be executed again."
            )

        # ======================================================
        # FAILED AFTER ALL RETRIES
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