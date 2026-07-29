
from __future__ import annotations

from typing import Any

from app.agents.planner import PlannerAgent
from app.agents.coder import CoderAgent
from app.agents.reviewer import ReviewerAgent

from app.builders.project_builder import ProjectBuilder
from app.validators.project_validator import ProjectValidator

from app.models.task import Task
from app.core.logger import logger

from app.database.database import SessionLocal
from app.database.crud import create_project

from app.services.retry.retry_manager import RetryManager
from app.services.testing.test_manager import TestManager

from app.websocket.manager import manager


class AgentOrchestrator:
    """
    Main autonomous workflow controller for AutoDev AI.

    Pipeline:

        User Request
            ↓
        Planner Agent
            ↓
        Coder Agent
            ↓
        Project Builder
            ↓
        Execution / Retry Manager
            ↓
        Project Validation
            ↓
        Automated Testing
            ↓
        AI Review
            ↓
        Self-Healing when required
            ↓
        Database Save
            ↓
        Final Result
    """

    TOTAL_STEPS = 9

    def __init__(self) -> None:
        self.planner = PlannerAgent()
        self.coder = CoderAgent()
        self.reviewer = ReviewerAgent()

        self.builder = ProjectBuilder()
        self.validator = ProjectValidator()

        self.retry_manager = RetryManager()
        self.tester = TestManager()

    # ==========================================================
    # PROGRESS HELPER
    # ==========================================================

    async def _progress(
        self,
        session_id: str | None,
        step: str,
        progress: int,
        message: str,
    ) -> None:
        """
        Send websocket progress safely.

        Failure to update the UI should never crash the
        AutoDev AI pipeline.
        """

        if not session_id:
            return

        try:
            await manager.send_progress(
                session_id=session_id,
                step=step,
                progress=progress,
                message=message,
            )

        except Exception:
            logger.exception(
                "Failed to send websocket progress."
            )

    # ==========================================================
    # DEFAULT RESULT HELPERS
    # ==========================================================

    @staticmethod
    def _failed_test_result(
        message: str,
    ) -> dict[str, Any]:
        return {
            "success": False,
            "stdout": "",
            "stderr": message,
            "return_code": -1,
            "execution_time": 0,
        }

    @staticmethod
    def _failed_review(
        error: str,
    ) -> dict[str, Any]:
        return {
            "success": False,
            "error": error,
        }

    @staticmethod
    def _failed_validation(
        error: str,
    ) -> dict[str, Any]:
        return {
            "valid": False,
            "errors": [error],
            "warnings": [],
        }

    # ==========================================================
    # MAIN PIPELINE
    # ==========================================================

    async def execute(
        self,
        task: str,
        history: list | None = None,
        session_id: str | None = None,
    ) -> dict[str, Any]:

        logger.info("=" * 60)
        logger.info("Starting AutoDev AI Pipeline")
        logger.info("=" * 60)

        if not task or not task.strip():
            raise ValueError(
                "Task cannot be empty."
            )

        plan: Task | None = None
        code: str = ""
        project: dict[str, Any] = {}

        execution_result: dict[str, Any] = {}
        validation: dict[str, Any] = {}
        test_result: dict[str, Any] = {}
        review: dict[str, Any] = {}
        debug_report: dict[str, Any] = {}

        # ======================================================
        # STEP 1 - PLANNING
        # ======================================================

        logger.info(
            "Step 1/9 - Planning..."
        )

        await self._progress(
            session_id,
            "Planning",
            10,
            "Generating implementation plan...",
        )

        try:
            plan = await self.planner.run(
                task,
                history,
            )

        except Exception:
            logger.exception(
                "Planner Agent failed."
            )
            raise

        if plan is None:
            raise RuntimeError(
                "Planner failed to generate a task."
            )

        logger.info(
            f"Planning completed: {plan.title}"
        )

        await self._progress(
            session_id,
            "Planning",
            20,
            "Planning completed.",
        )

        # ======================================================
        # STEP 2 - CODING
        # ======================================================

        logger.info(
            "Step 2/9 - Generating code..."
        )

        await self._progress(
            session_id,
            "Coding",
            25,
            "Generating source code...",
        )

        try:
            code = await self.coder.run(
                plan
            )

        except Exception:
            logger.exception(
                "Coder Agent failed."
            )
            raise

        if not code or not code.strip():
            raise RuntimeError(
                "Coder failed to generate source code."
            )

        logger.info(
            f"Generated {len(code)} characters of source code."
        )

        await self._progress(
            session_id,
            "Coding",
            35,
            "Source code generated.",
        )

        # ======================================================
        # STEP 3 - BUILD PROJECT
        # ======================================================

        logger.info(
            "Step 3/9 - Building project..."
        )

        await self._progress(
            session_id,
            "Building",
            40,
            "Creating project structure...",
        )

        try:
            project = self.builder.build(
                project_name=plan.title,
                llm_output=code,
            )

        except Exception:
            logger.exception(
                "Project Builder failed."
            )
            raise

        if not project:
            raise RuntimeError(
                "Project Builder returned no result."
            )

        if not project.get("project_path"):
            raise RuntimeError(
                "Project Builder did not return project_path."
            )

        if not project.get("zip_path"):
            raise RuntimeError(
                "Project Builder did not return zip_path."
            )

        logger.info(
            f"Project created at: "
            f"{project['project_path']}"
        )

        await self._progress(
            session_id,
            "Building",
            50,
            "Project built successfully.",
        )

        # ======================================================
        # STEP 4 - EXECUTION
        # ======================================================

        logger.info(
            "Step 4/9 - Executing project..."
        )

        await self._progress(
            session_id,
            "Execution",
            55,
            "Executing generated project...",
        )

        try:
            retry_result = (
                await self.retry_manager.execute_with_retry(
                    project=project,
                    code=code,
                )
            )

        except Exception:
            logger.exception(
                "Project execution failed."
            )

            execution_result = {
                "success": False,
                "stdout": "",
                "stderr": "Project execution failed.",
                "return_code": -1,
            }

            debug_report = {
                "success": False,
                "error": "Project execution failed.",
            }

            retry_result = None

        if retry_result is not None:

            if not isinstance(
                retry_result,
                tuple,
            ) or len(retry_result) != 4:

                raise RuntimeError(
                    "RetryManager returned invalid result. "
                    "Expected: "
                    "(execution_result, project, code, debug_report)"
                )

            (
                execution_result,
                project,
                code,
                debug_report,
            ) = retry_result

            execution_result = (
                execution_result
                or {}
            )

            debug_report = (
                debug_report
                or {}
            )

        logger.info(
            "Execution stage completed."
        )

        await self._progress(
            session_id,
            "Execution",
            65,
            "Execution completed.",
        )

        # ======================================================
        # STEP 5 - VALIDATION
        # ======================================================

        logger.info(
            "Step 5/9 - Validating project..."
        )

        await self._progress(
            session_id,
            "Validation",
            70,
            "Validating generated project...",
        )

        try:
            validation = self.validator.validate(
                project["project_path"]
            )

            validation = (
                validation
                or {}
            )

            logger.info(
                "Project validation completed."
            )

        except Exception as exc:
            logger.exception(
                "Project validation failed."
            )

            validation = self._failed_validation(
                str(exc)
            )

        await self._progress(
            session_id,
            "Validation",
            75,
            "Validation completed.",
        )

        # ======================================================
        # STEP 6 - AUTOMATED TESTING
        # ======================================================

        logger.info(
            "Step 6/9 - Running automated tests..."
        )

        await self._progress(
            session_id,
            "Testing",
            80,
            "Running automated tests...",
        )

        if (
            execution_result
            and execution_result.get("success")
        ):

            try:
                test_result = self.tester.run(
                    project["project_path"]
                )

                test_result = (
                    test_result
                    or self._failed_test_result(
                        "Test manager returned no result."
                    )
                )

                logger.info(
                    "Automated testing completed."
                )

            except Exception as exc:
                logger.exception(
                    "Automated testing failed."
                )

                test_result = (
                    self._failed_test_result(
                        str(exc)
                    )
                )

        else:

            logger.warning(
                "Skipping automated tests because "
                "project execution failed."
            )

            test_result = (
                self._failed_test_result(
                    "Execution failed. Tests skipped."
                )
            )

        await self._progress(
            session_id,
            "Testing",
            85,
            "Testing completed.",
        )

        # ======================================================
        # STEP 7 - AI REVIEW
        # ======================================================

        logger.info(
            "Step 7/9 - AI Review..."
        )

        await self._progress(
            session_id,
            "Review",
            90,
            "AI is reviewing the generated project...",
        )

        try:

            # The current ReviewerAgent interface accepts
            # the generated code string.
            review = await self.reviewer.run(
                code
            )

            review = (
                review
                or {}
            )

            logger.info(
                "AI review completed."
            )

        except Exception as exc:

            logger.exception(
                "Reviewer Agent failed."
            )

            review = self._failed_review(
                str(exc)
            )

        await self._progress(
            session_id,
            "Review",
            95,
            "AI review completed.",
        )

        # ======================================================
        # STEP 8 - SELF HEALING
        # ======================================================

        logger.info(
            "Step 8/9 - Self-Healing..."
        )

        execution_success = bool(
            execution_result
            and execution_result.get(
                "success"
            )
        )

        test_success = bool(
            test_result
            and test_result.get(
                "success"
            )
        )

        validation_success = bool(
            validation
            and validation.get(
                "valid",
                False,
            )
        )

        needs_repair = not (
            execution_success
            and test_success
            and validation_success
        )

        if needs_repair:

            logger.warning(
                "Project quality checks failed. "
                "Starting self-healing..."
            )

            await self._progress(
                session_id,
                "Self-Healing",
                96,
                "Problems detected. Repairing project...",
            )

            try:

                repair_result = (
                    await self.retry_manager.execute_with_retry(
                        project=project,
                        code=code,
                        review=review,
                    )
                )

            except Exception:

                logger.exception(
                    "Self-healing failed."
                )

                repair_result = None

            if repair_result is not None:

                if not isinstance(
                    repair_result,
                    tuple,
                ) or len(repair_result) != 4:

                    logger.error(
                        "Self-healing returned invalid result."
                    )

                else:

                    (
                        execution_result,
                        project,
                        code,
                        debug_report,
                    ) = repair_result

                    execution_result = (
                        execution_result
                        or {}
                    )

                    debug_report = (
                        debug_report
                        or {}
                    )

                    # ------------------------------------------
                    # Re-validation
                    # ------------------------------------------

                    try:

                        validation = (
                            self.validator.validate(
                                project[
                                    "project_path"
                                ]
                            )
                            or {}
                        )

                        logger.info(
                            "Validation completed after repair."
                        )

                    except Exception as exc:

                        logger.exception(
                            "Validation failed after repair."
                        )

                        validation = (
                            self._failed_validation(
                                str(exc)
                            )
                        )

                    # ------------------------------------------
                    # Re-testing
                    # ------------------------------------------

                    if execution_result.get(
                        "success"
                    ):

                        try:

                            test_result = (
                                self.tester.run(
                                    project[
                                        "project_path"
                                    ]
                                )
                                or {}
                            )

                            logger.info(
                                "Testing completed after repair."
                            )

                        except Exception as exc:

                            logger.exception(
                                "Testing failed after repair."
                            )

                            test_result = (
                                self._failed_test_result(
                                    str(exc)
                                )
                            )

                    else:

                        test_result = (
                            self._failed_test_result(
                                "Execution failed after repair."
                            )
                        )

                    # ------------------------------------------
                    # Re-review
                    # ------------------------------------------

                    try:

                        review = (
                            await self.reviewer.run(
                                code
                            )
                            or {}
                        )

                        logger.info(
                            "Review completed after repair."
                        )

                    except Exception as exc:

                        logger.exception(
                            "Reviewer failed after repair."
                        )

                        review = (
                            self._failed_review(
                                str(exc)
                            )
                        )

                    # ------------------------------------------
                    # Final repair status
                    # ------------------------------------------

                    if (
                        execution_result.get(
                            "success"
                        )
                        and test_result.get(
                            "success"
                        )
                        and validation.get(
                            "valid",
                            False,
                        )
                    ):

                        logger.info(
                            "Self-healing succeeded. "
                            "Project now passes quality checks."
                        )

                    else:

                        logger.warning(
                            "Self-healing completed, but "
                            "the project still has failures."
                        )

            else:

                logger.error(
                    "Self-healing did not return a result."
                )

        else:

            logger.info(
                "Execution, validation and tests passed. "
                "Self-healing skipped."
            )

        # ======================================================
        # STEP 9 - SAVE PROJECT
        # ======================================================

        logger.info(
            "Step 9/9 - Saving project..."
        )

        await self._progress(
            session_id,
            "Saving",
            98,
            "Saving project information...",
        )

        db = SessionLocal()

        try:

            create_project(
                db=db,
                session_id=session_id or "default",
                title=plan.title,
                prompt=task,
                project_path=project[
                    "project_path"
                ],
                zip_path=project[
                    "zip_path"
                ],
            )

            logger.info(
                "Project saved successfully."
            )

        except Exception:

            # Database failure should not destroy
            # the generated project.
            logger.exception(
                "Failed to save project to database."
            )

        finally:

            db.close()

        # ======================================================
        # COMPLETED
        # ======================================================

        await self._progress(
            session_id,
            "Completed",
            100,
            "Project generation completed.",
        )

        logger.info("=" * 60)
        logger.info(
            "AutoDev AI Pipeline Finished"
        )
        logger.info("=" * 60)

        # ------------------------------------------------------
        # Normalize results
        # ------------------------------------------------------

        execution_result = (
            execution_result
            or {}
        )

        validation = (
            validation
            or {}
        )

        test_result = (
            test_result
            or {}
        )

        review = (
            review
            or {}
        )

        debug_report = (
            debug_report
            or {}
        )

        # ------------------------------------------------------
        # Final result
        # ------------------------------------------------------

        return {
            "success": bool(
                execution_result.get(
                    "success",
                    False,
                )
                and validation.get(
                    "valid",
                    False,
                )
                and test_result.get(
                    "success",
                    False,
                )
            ),

            "plan": plan.model_dump(),

            "project": project,

            "execution": execution_result,

            "validation": validation,

            "tests": test_result,

            "debug_report": debug_report,

            "review": review,

            "improved_code": code,
        }
