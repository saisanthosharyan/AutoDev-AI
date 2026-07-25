from app.core.logger import logger

from app.agents.planner import PlannerAgent
from app.agents.coder import CoderAgent
from app.agents.reviewer import ReviewerAgent

from app.builders.project_builder import ProjectBuilder
from app.services.retry.retry_manager import RetryManager
from app.services.evaluation.evaluation_manager import EvaluationManager

from app.agents.memory import Memory


class Workflow:
    """
    Executes the complete AutoDev-AI workflow.
    """

    def __init__(self):

        self.memory = Memory()

        self.planner = PlannerAgent()
        self.coder = CoderAgent()
        self.reviewer = ReviewerAgent()

        self.builder = ProjectBuilder()
        self.retry = RetryManager()
        self.evaluator = EvaluationManager()

    async def run(self, prompt: str):

        logger.info("=" * 60)
        logger.info("Starting AutoDev-AI Workflow")
        logger.info("=" * 60)

        state = self.memory.load()

        # ------------------------------------------
        # User Prompt
        # ------------------------------------------

        state.prompt = prompt

        # ------------------------------------------
        # Planning
        # ------------------------------------------

        logger.info("Planning project...")

        state.plan = await self.planner.run(prompt)

        # ------------------------------------------
        # Code Generation
        # ------------------------------------------

        logger.info("Generating project...")

        state.code = await self.coder.run(
            prompt=prompt,
            plan=state.plan,
        )

        # ------------------------------------------
        # Build Project
        # ------------------------------------------

        logger.info("Building project...")

        state.project = self.builder.build(
            state.code
        )

        # ------------------------------------------
        # Review
        # ------------------------------------------

        logger.info("Reviewing project...")

        state.review = await self.reviewer.run(
            state.code
        )

        # ------------------------------------------
        # Execute + Retry
        # ------------------------------------------

        logger.info("Executing project...")

        (
            state.execution,
            state.project,
            state.code,
            state.debug_report,
        ) = await self.retry.execute_with_retry(
            project=state.project,
            code=state.code,
            review=state.review,
        )

        # ------------------------------------------
        # Evaluation
        # ------------------------------------------

        logger.info("Evaluating project...")

        state.evaluation = self.evaluator.evaluate(
            state.project,
            state.code,
        )

        state.score = state.evaluation.get(
            "overall_score",
            0,
        )

        state.success = state.execution.get(
            "success",
            False,
        )

        self.memory.save(state)

        logger.info("=" * 60)
        logger.info("Workflow Finished")
        logger.info("=" * 60)

        return state