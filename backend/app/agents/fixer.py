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
You are an Expert Software Engineer responsible for repairing AI-generated software projects.

The generated project has already been reviewed and executed.

========================
REVIEWER FEEDBACK
========================

{review}

========================
RUNTIME EXECUTION ERROR
========================

{execution_error}

========================
CURRENT PROJECT
========================

{code}

========================
YOUR TASK
========================

1. Analyze the runtime error carefully.
2. Fix all syntax errors.
3. Fix all runtime errors.
4. Fix all logical errors.
5. Apply every valid reviewer suggestion.
6. Preserve the existing project architecture.
7. Do NOT remove existing features unless absolutely necessary.
8. Do NOT rename files unless required.
9. Return the COMPLETE corrected project.

IMPORTANT:
- Return ONLY the project files.
- Do NOT include explanations.
- Do NOT use Markdown code fences.
- Do NOT add extra text before or after the project.
"""

        logger.info("Starting AI project repair...")

        response = await llm.generate(prompt)

        logger.info("Project repair completed successfully.")

        return response