from app.agents.planner import PlannerAgent
from app.agents.coder import CoderAgent
from app.agents.reviewer import ReviewerAgent
from app.agents.fixer import FixerAgent

from app.builders.project_builder import ProjectBuilder
from app.validators.project_validator import ProjectValidator

from app.models.task import Task
from app.core.logger import logger

from app.database.database import SessionLocal
from app.database.crud import create_project

from app.services.execution.execution_manager import ExecutionManager
from app.services.debugger.debug_manager import DebugManager
from app.services.testing.test_manager import TestManager


MAX_RETRIES = 3


class AgentOrchestrator:

    def __init__(self):
        self.planner = PlannerAgent()
        self.coder = CoderAgent()
        self.reviewer = ReviewerAgent()
        self.fixer = FixerAgent()

        self.builder = ProjectBuilder()
        self.validator = ProjectValidator()
        self.executor = ExecutionManager()
        self.debugger = DebugManager()
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

        plan: Task = await self.planner.run(
            task,
            history,
        )

        logger.info("Planning completed successfully.")

        # ---------------------------------------------------
        # Step 2 - Code Generation
        # ---------------------------------------------------

        logger.info("Step 2/8 - Generating source code...")

        code = await self.coder.run(plan)

        logger.info(
            f"Generated {len(code)} characters."
        )

        # ---------------------------------------------------
        # Step 3 - Build Project
        # ---------------------------------------------------

        logger.info("Step 3/8 - Building project...")

        project = self.builder.build(
            plan.title,
            code,
        )

        logger.info(
            f"Project created at {project['project_path']}"
        )

        # ---------------------------------------------------
        # Step 4 - Execute Project
        # ---------------------------------------------------

        logger.info("Step 4/8 - Executing project...")

        execution_result = None

        for attempt in range(1, MAX_RETRIES + 1):

            logger.info(
                f"Execution Attempt {attempt}/{MAX_RETRIES}"
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
                }

            if execution_result.get("success"):
                logger.info("Execution successful.")
                break

            logger.warning("Execution failed.")

            debug_report = self.debugger.analyze(
                execution_result
            )

            try:

                fixed_code = await self.fixer.run(
                    code=code,
                    review="",
                    execution_error=debug_report,
                )

                code = fixed_code

                project = self.builder.rebuild(
                    project["project_path"],
                    fixed_code,
                )

            except Exception:

                logger.exception(
                    "Automatic repair failed."
                )
                break

        debug_report = self.debugger.analyze(
            execution_result
        )
                # ---------------------------------------------------
        # Step 5 - Save Project
        # ---------------------------------------------------

        logger.info("Step 5/8 - Saving project...")

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

        # ---------------------------------------------------
        # Step 6 - Validate Project
        # ---------------------------------------------------

        logger.info("Step 6/8 - Validating project...")

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

        # ---------------------------------------------------
        # Step 7 - Run Tests
        # ---------------------------------------------------

        logger.info("Step 7/8 - Running tests...")

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

        # ---------------------------------------------------
        # AI Code Review
        # ---------------------------------------------------

        logger.info("Reviewing generated project...")

        try:

            review = await self.reviewer.run(code)

            logger.info("Review completed.")

        except Exception as e:

            logger.exception("Reviewer failed.")

            review = str(e)
        # ---------------------------------------------------
        # Step 8 - Improve Project (Self-Healing)
        # ---------------------------------------------------

        logger.info("Step 8/8 - Improving project...")

        fixed_code = code

        for attempt in range(1, MAX_RETRIES + 1):

            if execution_result.get("success") and test_result.get("success"):
                logger.info("Project already passed execution and tests.")
                break

            logger.info(f"Repair Attempt {attempt}/{MAX_RETRIES}")

            try:

                fixed_code = await self.fixer.run(
                    code=fixed_code,
                    review=review,
                    execution_error=debug_report,
                )

                project = self.builder.rebuild(
                    project["project_path"],
                    fixed_code,
                )

                execution_result = self.executor.run(
                    project["project_path"]
                )

                test_result = self.tester.run(
                    project["project_path"]
                )

                debug_report = self.debugger.analyze(
                    execution_result
                )

                if execution_result.get("success") and test_result.get("success"):

                    logger.info("Project repaired successfully.")

                    break

            except Exception:

                logger.exception("Repair attempt failed.")

                break

        logger.info("=" * 60)
        logger.info("AutoDev AI Pipeline Finished Successfully")
        logger.info("=" * 60)

        return {
            "plan": plan.model_dump(),
            "project": project,
            "execution": execution_result,
            "validation": validation,
            "tests": test_result,
            "debug_report": debug_report,
            "review": review,
            "improved_code": fixed_code,
        }