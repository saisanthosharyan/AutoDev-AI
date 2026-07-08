from app.agents.planner import PlannerAgent
from app.agents.coder import CoderAgent
from app.agents.reviewer import ReviewerAgent
from app.agents.fixer import FixerAgent

from app.models.task import Task


class AgentOrchestrator:

    def __init__(self):
        self.planner = PlannerAgent()
        self.coder = CoderAgent()
        self.reviewer = ReviewerAgent()
        self.fixer = FixerAgent()

    async def execute(
        self,
        task: str,
        history: list | None = None
    ):

        # Step 1
        plan: Task = await self.planner.run(
            task,
            history
        )

        # Step 2
        generated_code = await self.coder.run(plan)

        # Step 3
        review = await self.reviewer.run(
            generated_code
        )

        # Step 4
        improved_code = await self.fixer.run(
            generated_code,
            review
        )

        return {
            "plan": plan.model_dump(),
            "code": generated_code,
            "review": review,
            "improved_code": improved_code
        }