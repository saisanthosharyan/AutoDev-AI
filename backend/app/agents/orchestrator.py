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
        history: list = None,
        session_id: str | None = None,
    ):

        logger.info("=" * 60)
        logger.info("Starting AutoDev AI Pipeline")
        logger.info("=" * 60)

        # ---------------------------------------------------
        # Step 1 - Planning
        # ---------------------------------------------------

        logger.info("Step 1/8 - Planning...")

        if session_id:
            await manager.send_progress(
                session_id=session_id,
                step="Planning",
                progress=10,
                message="Generating implementation plan..."
            )

        plan: Task = await self.planner.run(
            task,
            history,
        )

        logger.info("Planning completed successfully.")

        if session_id:
            await manager.send_progress(
                session_id=session_id,
                step="Planning",
                progress=20,
                message="Planning completed."
            )

        # ---------------------------------------------------
        # Step 2 - Generate Code
        # ---------------------------------------------------

        logger.info("Step 2/8 - Generating source code...")

        if session_id:
            await manager.send_progress(
                session_id=session_id,
                step="Coding",
                progress=25,
                message="Generating project source code..."
            )

        code = await self.coder.run(
            plan
        )

        logger.info(
            f"Generated {len(code)} characters."
        )
        if session_id:
            await manager.send_progress(
                session_id=session_id,
                step="Coding",
                progress=35,
                message="Source code generated successfully."
            )

        # ---------------------------------------------------
        # Step 3 - Build Project
        # ---------------------------------------------------

        logger.info("Step 3/8 - Building project...")

        if session_id:
            await manager.send_progress(
                session_id=session_id,
                step="Building",
                progress=40,
                message="Building project structure..."
            )

        project = self.builder.build(
            plan.title,
            code,
        )

        logger.info(
            f"Project created at {project['project_path']}"
        )
        if session_id:
            await manager.send_progress(
                session_id=session_id,
                step="Building",
                progress=50,
                message="Project structure created successfully."
            )
        # ---------------------------------------------------
        # Step 4 - Execute Project
        # ---------------------------------------------------

        logger.info("Step 4/8 - Executing project...")

        if session_id:
            await manager.send_progress(
                session_id=session_id,
                step="Execution",
                progress=55,
                message="Executing generated project..."
            )

        (
            execution_result,
            project,
            code,
            debug_report,
        ) = await self.retry_manager.execute_with_retry(
            project=project,
            code=code,
        )
        if session_id:
            await manager.send_progress(
                session_id=session_id,
                step="Execution",
                progress=65,
                message="Project executed successfully."
            )

        # ---------------------------------------------------
        # Step 5 - Save Project
        # ---------------------------------------------------

        logger.info("Step 5/8 - Saving project...")

        if session_id:
            await manager.send_progress(
                session_id=session_id,
                step="Saving",
                progress=66,
                message="Saving project information..."
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

            logger.info("Project saved successfully.")

        finally:

            db.close()
        if session_id:
            await manager.send_progress(
                session_id=session_id,
                step="Saving",
                progress=70,
                message="Project saved successfully."
            )

        # ---------------------------------------------------
        # Step 6 - Validate
        # ---------------------------------------------------

        logger.info("Step 6/8 - Validating project...")

        if session_id:
            await manager.send_progress(
                session_id=session_id,
                step="Validation",
                progress=75,
                message="Validating generated project..."
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
                progress=80,
                message="Validation completed."
            )
        

        # ---------------------------------------------------
        # Step 7 - Run Tests
        # ---------------------------------------------------

        logger.info("Step 7/8 - Running tests...")

        if session_id:
            await manager.send_progress(
                session_id=session_id,
                step="Testing",
                progress=85,
                message="Running automated tests..."
            )

        if execution_result.get("success"):

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
                "stderr": "Tests skipped because execution failed.",
                "return_code": -1,
                "execution_time": 0,
            }
        if session_id:
            await manager.send_progress(
                session_id=session_id,
                step="Review",
                progress=92,
                message="AI is reviewing the generated project..."
            )
        # ---------------------------------------------------
        # AI Review
        # ---------------------------------------------------

        logger.info("Reviewing generated project...")

        if session_id:
            await manager.send_progress(
                session_id=session_id,
                step="Review",
                progress=95,
                message="AI review completed."
            )

        try:

            review = await self.reviewer.run(code)

            logger.info("Review completed.")

        except Exception as e:

            logger.exception("Reviewer failed.")

            review = str(e)

        # ---------------------------------------------------
        # Step 8 - Final Self Healing
        # ---------------------------------------------------

        logger.info("Step 8/8 - Final self-healing...")

        # Only perform self-healing if execution or tests failed
        if not (
            execution_result.get("success")
            and test_result.get("success")
        ):

            logger.warning(
                "Issues detected. Starting self-healing process..."
            )

            if session_id:
                await manager.send_progress(
                    session_id=session_id,
                    step="Self-Healing",
                    progress=96,
                    message="Fixing any remaining issues..."
                )

            (
                execution_result,
                project,
                code,
                debug_report,
            ) = await self.retry_manager.execute_with_retry(
                project=project,
                code=code,
                review=review,
            )

            if execution_result.get("success"):

                logger.info(
                    "Self-healing completed successfully."
                )

                try:

                    test_result = self.tester.run(
                        project["project_path"]
                    )

                    logger.info(
                        "Testing completed after repair."
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

            else:

                logger.error(
                    "Self-healing failed. Project still contains errors."
                )

        else:

            logger.info(
                "Project passed execution and testing. Self-healing skipped."
            )
        # ---------------------------------------------------
        # Completed
        # ---------------------------------------------------

        if session_id:
            await manager.send_progress(
                session_id=session_id,
                step="Completed",
                progress=100,
                message="Project generated successfully 🎉"
            )

        logger.info("=" * 60)
        logger.info(
            "AutoDev AI Pipeline Finished Successfully"
        )
        logger.info("=" * 60)

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