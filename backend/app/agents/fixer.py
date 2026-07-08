from app.services.llm.router import LLMRouter
from app.agents.base_agent import BaseAgent


class FixerAgent(BaseAgent):

    async def run(self, code: str, review: str):

        llm = LLMRouter.get_llm()

        prompt = f"""
You are a Senior Software Engineer.

The following code has already been reviewed.

Review Feedback:

{review}

Original Code:

{code}

Rewrite the code by fixing every issue.

Return ONLY the improved code.
"""

        return await llm.generate(prompt)