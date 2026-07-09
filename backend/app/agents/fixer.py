from app.services.llm.router import LLMRouter
from app.agents.base_agent import BaseAgent
from app.core.logger import logger


class FixerAgent(BaseAgent):

    async def run(
        self,
        code: str,
        review: str
    ):

        llm = LLMRouter.get_llm()

        prompt = f"""
You are an Expert Software Engineer.

Below is the generated project.

{code}

Below is the review.

{review}

Improve the project using every suggestion.

Return ONLY the improved project files.

Do not explain anything.
"""

        logger.info("Improving project...")

        response = await llm.generate(prompt)

        logger.info("Fixer completed successfully.")

        return response