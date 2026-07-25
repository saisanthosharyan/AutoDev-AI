from app.core.logger import logger

from app.agents.state import AgentState


class Memory:
    """
    Stores the current workflow state for AutoDev-AI.

    All agents read from and write to this shared memory.
    """

    def __init__(self):

        self.state = AgentState()

    # --------------------------------------------------

    def load(self) -> AgentState:
        """
        Return the current state.
        """

        return self.state

    # --------------------------------------------------

    def save(self, state: AgentState):

        logger.info("Saving workflow state.")

        self.state = state

    # --------------------------------------------------

    def reset(self):

        logger.info("Resetting workflow memory.")

        self.state = AgentState()

    # --------------------------------------------------
    # Helper Methods
    # --------------------------------------------------

    def update_prompt(self, prompt: str):

        self.state.prompt = prompt

    def update_plan(self, plan: str):

        self.state.plan = plan

    def update_code(self, code: str):

        self.state.code = code

    def update_project(self, project: dict):

        self.state.project = project

    def update_review(self, review: str):

        self.state.review = review

    def update_execution(self, execution: dict):

        self.state.execution = execution

    def update_debug(self, report: str):

        self.state.debug_report = report

    def update_evaluation(self, evaluation: dict):

        self.state.evaluation = evaluation

        self.state.score = evaluation.get(
            "overall_score",
            0,
        )

    def increment_retry(self):

        self.state.retry_count += 1

    def mark_success(self):

        self.state.success = True

    def mark_failure(self):

        self.state.success = False