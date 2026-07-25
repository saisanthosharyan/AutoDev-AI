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

    def __init__(self):

        self.planner = PlannerAgent()
        self.coder = CoderAgent()
        self.reviewer = ReviewerAgent()

        self.builder = ProjectBuilder()
        self.validator = ProjectValidator()

        self.retry_manager = RetryManager()
        self.tester = TestManager()

    async def execute(
        self,
        task: str,
        history: list | None = None,
        session_id: str | None = None,
    ):

        logger.info("=" * 60)
        logger.info("Starting AutoDev AI Pipeline")
        logger.info("=" * 60)

        # =====================================================
        # STEP 1 - PLANNING
        # =====================================================

        logger.info("Step 1/8 - Planning...")

        if session_id:
            await manager.send_progress(
                session_id=session_id,
                step="Planning",
                progress=10,
                message="Generating implementation plan...",
            )

        plan: Task = await self.planner.run(task, history)

        if plan is None:
            raise RuntimeError("Planner failed to generate task.")

        logger.info("Planning completed.")

        if session_id:
            await manager.send_progress(
                session_id=session_id,
                step="Planning",
                progress=20,
                message="Planning completed.",
            )

        # =====================================================
        # STEP 2 - GENERATE CODE
        # =====================================================

        logger.info("Step 2/8 - Generating code...")

        if session_id:
            await manager.send_progress(
                session_id=session_id,
                step="Coding",
                progress=25,
                message="Generating source code...",
            )

        code = await self.coder.run(plan)

        if not code:
            raise RuntimeError("Coder failed to generate source code.")

        logger.info(f"Generated {len(code)} characters.")

        if session_id:
            await manager.send_progress(
                session_id=session_id,
                step="Coding",
                progress=35,
                message="Source code generated.",
            )

        # =====================================================
        # STEP 3 - BUILD PROJECT
        # =====================================================

        logger.info("Step 3/8 - Building project...")

        if session_id:
            await manager.send_progress(
                session_id=session_id,
                step="Building",
                progress=40,
                message="Creating project structure...",
            )

        try:
            project = self.builder.build(
                plan.title,
                code,
            )

        except Exception as e:
            logger.exception("Project Builder failed.")
            raise RuntimeError(str(e))

        if (
            not project
            or "project_path" not in project
            or "zip_path" not in project
        ):
            raise RuntimeError("Project Builder returned invalid data.")

        logger.info(
            f"Project created at {project['project_path']}"
        )

        if session_id:
            await manager.send_progress(
                session_id=session_id,
                step="Building",
                progress=50,
                message="Project built successfully.",
            )
        # =====================================================
        # STEP 4 - EXECUTE PROJECT
        # =====================================================

        logger.info("Step 4/9 - Executing project...")

        if session_id:
            await manager.send_progress(
                session_id=session_id,
                step="Execution",
                progress=55,
                message="Executing generated project...",
            )

        retry_result = await self.retry_manager.execute_with_retry(
            project=project,
            code=code,
        )

        if retry_result is None:
            raise RuntimeError(
                "RetryManager returned no result."
            )

        (
            execution_result,
            project,
            code,
            debug_report,
        ) = retry_result

        logger.info("Execution completed.")

        if session_id:
            await manager.send_progress(
                session_id=session_id,
                step="Execution",
                progress=65,
                message="Execution completed.",
            )

        # =====================================================
        # STEP 5 - VALIDATE PROJECT
        # =====================================================

        logger.info("Step 5/9 - Validating project...")

        if session_id:
            await manager.send_progress(
                session_id=session_id,
                step="Validation",
                progress=70,
                message="Validating generated project...",
            )

        try:

            validation = self.validator.validate(
                project["project_path"]
            )

            logger.info("Validation completed.")

        except Exception as e:

            logger.exception("Validation failed.")

            validation = {
                "valid": False,
                "errors": [str(e)],
                "warnings": [],
            }

        if session_id:
            await manager.send_progress(
                session_id=session_id,
                step="Validation",
                progress=75,
                message="Validation completed.",
            )

        # =====================================================
        # STEP 6 - RUN TESTS
        # =====================================================

        logger.info("Step 6/9 - Running automated tests...")

        if session_id:
            await manager.send_progress(
                session_id=session_id,
                step="Testing",
                progress=80,
                message="Running automated tests...",
            )

        if execution_result and execution_result.get("success"):

            try:

                test_result = self.tester.run(
                    project["project_path"]
                )

                logger.info("Testing completed.")

            except Exception as e:

                logger.exception("Testing failed.")

                test_result = {
                    "success": False,
                    "stdout": "",
                    "stderr": str(e),
                    "return_code": -1,
                    "execution_time": 0,
                }

        else:

            logger.warning(
                "Skipping tests because execution failed."
            )

            test_result = {
                "success": False,
                "stdout": "",
                "stderr": "Execution failed. Tests skipped.",
                "return_code": -1,
                "execution_time": 0,
            }

        if session_id:
            await manager.send_progress(
                session_id=session_id,
                step="Testing",
                progress=85,
                message="Testing completed.",
            )

        # =====================================================
        # STEP 7 - AI REVIEW
        # =====================================================

        logger.info("Step 7/9 - AI Review...")

        if session_id:
            await manager.send_progress(
                session_id=session_id,
                step="Review",
                progress=90,
                message="AI is reviewing the project...",
            )

        try:

            review = await self.reviewer.run(code)

            logger.info("Review completed.")

        except Exception as e:

            logger.exception("Reviewer failed.")

            review = {
                "success": False,
                "error": str(e),
            }

        if session_id:
            await manager.send_progress(
                session_id=session_id,
                step="Review",
                progress=95,
                message="AI review completed.",
            )
                # =====================================================
        # STEP 8 - SELF HEALING
        # =====================================================

        logger.info("Step 8/9 - Self Healing...")

        if not (
            execution_result
            and execution_result.get("success")
            and test_result
            and test_result.get("success")
        ):

            logger.warning(
                "Problems detected. Starting self-healing..."
            )

            if session_id:
                await manager.send_progress(
                    session_id=session_id,
                    step="Self-Healing",
                    progress=96,
                    message="Repairing project...",
                )

            retry_result = await self.retry_manager.execute_with_retry(
                project=project,
                code=code,
                review=review,
            )

            if retry_result is None:

                logger.error(
                    "RetryManager returned no result."
                )

            else:

                (
                    execution_result,
                    project,
                    code,
                    debug_report,
                ) = retry_result

                if execution_result.get("success"):

                    logger.info(
                        "Project repaired successfully."
                    )

                    # -----------------------------------------
                    # Re-Validate
                    # -----------------------------------------

                    try:

                        validation = self.validator.validate(
                            project["project_path"]
                        )

                        logger.info(
                            "Validation completed after repair."
                        )

                    except Exception as e:

                        logger.exception(
                            "Validation failed after repair."
                        )

                        validation = {
                            "valid": False,
                            "errors": [str(e)],
                            "warnings": [],
                        }

                    # -----------------------------------------
                    # Re-Test
                    # -----------------------------------------

                    try:

                        test_result = self.tester.run(
                            project["project_path"]
                        )

                        logger.info(
                            "Tests completed after repair."
                        )

                    except Exception as e:

                        logger.exception(
                            "Testing failed after repair."
                        )

                        test_result = {
                            "success": False,
                            "stdout": "",
                            "stderr": str(e),
                            "return_code": -1,
                            "execution_time": 0,
                        }

                    # -----------------------------------------
                    # Re-Review
                    # -----------------------------------------

                    try:

                        review = await self.reviewer.run(
                            code
                        )

                        logger.info(
                            "Review completed after repair."
                        )

                    except Exception as e:

                        logger.exception(
                            "Reviewer failed after repair."
                        )

                        review = {
                            "success": False,
                            "error": str(e),
                        }

                else:

                    logger.error(
                        "Self-healing could not repair the project."
                    )

        else:

            logger.info(
                "Execution and tests passed. Self-healing skipped."
            )

        # =====================================================
        # STEP 9 - SAVE PROJECT
        # =====================================================

        logger.info("Step 9/9 - Saving project...")

        if session_id:
            await manager.send_progress(
                session_id=session_id,
                step="Saving",
                progress=98,
                message="Saving project...",
            )

        db = SessionLocal()

        try:

            create_project(
                db=db,
                session_id=session_id or "default",
                title=plan.title,
                prompt=task,
                project_path=project["project_path"],
                zip_path=project["zip_path"],
            )

            logger.info(
                "Project saved successfully."
            )

        except Exception as e:

            logger.exception(
                f"Failed to save project: {e}"
            )

        finally:

            db.close()

        # =====================================================
        # COMPLETED
        # =====================================================

        if session_id:
            await manager.send_progress(
                session_id=session_id,
                step="Completed",
                progress=100,
                message="Project generated successfully 🎉",
            )

        logger.info("=" * 60)
        logger.info(
            "AutoDev AI Pipeline Finished Successfully"
        )
        logger.info("=" * 60)

        execution_result = execution_result or {}
        validation = validation or {}
        test_result = test_result or {}
        review = review or {}
        debug_report = debug_report or {}

        return {
            "plan": plan.model_dump(),
            "project": project,
            "execution": execution_result,
            "validation": validation,
            "tests": test_result,
            "debug_report": debug_report,
            "review": review,
            "improved_code": code,
        }