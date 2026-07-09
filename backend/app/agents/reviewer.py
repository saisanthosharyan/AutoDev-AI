from app.services.llm.router import LLMRouter
from app.agents.base_agent import BaseAgent
from app.core.logger import logger


class ReviewerAgent(BaseAgent):

    async def run(self, code: str):

        llm = LLMRouter.get_llm()

        prompt = f"""
You are a Senior Code Reviewer.

Review the following implementation.

Provide:

1. Strengths
2. Weaknesses
3. Bugs
4. Improvements
5. Final Score (/10)

Code:

{code}
"""

        logger.info("Reviewing generated project...")

        response = await llm.generate(prompt)

        logger.info("Reviewer completed successfully.")

        return response