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
        logger.info("Step 1/7 - Planning...")

        plan: Task = await self.planner.run(
            task,
            history,
        )

        logger.info("Planning completed successfully.")

        # ---------------------------------------------------
        # Step 2 - Code Generation
        # ---------------------------------------------------
        logger.info("Step 2/7 - Generating project source code...")

        code = await self.coder.run(plan)

        logger.info(
            f"Code generation completed ({len(code)} characters)."
        )

        # ---------------------------------------------------
        # Step 3 - Build Project
        # ---------------------------------------------------
        logger.info("Step 3/7 - Building project files...")

        project = self.builder.build(
            plan.title,
            code,
        )

        logger.info(
            f"Project created at: {project['project_path']}"
        )

        logger.info(
            f"Files created: {len(project['files'])}"
        )

        # ---------------------------------------------------
        # Step 4 - Execute Project
        # ---------------------------------------------------
        logger.info("Step 4/7 - Executing generated project...")

        try:
            execution_result = self.executor.run(
                project["project_path"]
            )

            logger.info("Execution completed successfully.")

        except Exception as e:
            logger.exception("Execution failed.")

            execution_result = {
                "success": False,
                "stdout": "",
                "stderr": str(e),
                "return_code": -1,
            }

        # ---------------------------------------------------
        # Save Project
        # ---------------------------------------------------
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

            logger.info("Project saved to database.")

        finally:
            db.close()

        # ---------------------------------------------------
        # Step 5 - Validate Project
        # ---------------------------------------------------
        logger.info("Step 5/7 - Validating generated project...")

        try:
            validation = self.validator.validate(
                project["project_path"]
            )

            logger.info("Validation completed successfully.")

        except Exception as e:
            logger.exception("Validation failed.")

            validation = {
                "valid": False,
                "errors": [str(e)],
                "warnings": [],
            }

        # ---------------------------------------------------
        # Step 6 - Review
        # ---------------------------------------------------
        logger.info("Step 6/7 - Reviewing generated project...")

        try:
            review = await self.reviewer.run(code)

            logger.info("Review completed successfully.")

        except Exception as e:
            logger.exception("Reviewer failed.")

            review = f"Reviewer failed: {e}"

        # ---------------------------------------------------
        # Step 7 - Improve
        # ---------------------------------------------------
        logger.info("Step 7/7 - Improving generated project...")

        try:
            fixed_code = await self.fixer.run(
                code,
                review,
            )

            logger.info("Project improvement completed successfully.")

        except Exception as e:
            logger.exception("Fixer failed.")

            fixed_code = code

        logger.info("=" * 60)
        logger.info("AutoDev AI Pipeline Finished Successfully")
        logger.info("=" * 60)

        return {
            "plan": plan.model_dump(),
            "project": project,
            "execution": execution_result,
            "validation": validation,
            "code": code,
            "review": review,
            "improved_code": fixed_code,
        }