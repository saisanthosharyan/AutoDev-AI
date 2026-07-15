from app.services.llm.router import LLMRouter
from app.agents.base_agent import BaseAgent
from app.core.logger import logger


class FixerAgent(BaseAgent):

    async def run(
        self,
        code: str,
        review: str,
        execution_error: str = "",
    ):

        llm = LLMRouter.get_llm()

        prompt = f"""
You are a Senior Software Engineer and Software Architect.

You are given a generated software project.

=========================
GENERATED PROJECT
=========================

{code}

=========================
CODE REVIEW
=========================

{review}

=========================
EXECUTION ERRORS
=========================

{execution_error}

Your responsibilities:

1. Fix every syntax error.
2. Fix every runtime error.
3. Fix import errors.
4. Fix dependency issues.
5. Fix missing files if required.
6. Improve code quality.
7. Improve project structure if necessary.
8. Preserve all existing functionality.
9. Do not remove working features.
10. Return the COMPLETE corrected project.

IMPORTANT:
- Return ONLY the corrected project files.
- Do NOT explain anything.
- Do NOT use markdown.
- Do NOT wrap the output inside triple backticks.
"""

        logger.info("Starting AI project repair...")

        response = await llm.generate(prompt)

        logger.info("Project repair completed successfully.")

        return response