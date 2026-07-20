from app.services.llm.router import LLMRouter
from app.core.logger import logger


class EditorAgent:
    """
    Responsible for repairing an existing project.

    Unlike the CoderAgent, this agent ONLY modifies files that need changes.
    """

    async def run(
        self,
        task: str,
        debug_report: str,
        project_structure: str,
    ) -> str:

        logger.info("Editing existing project...")

        prompt = f"""
You are a Senior Software Engineer.

Your job is NOT to regenerate the entire project.

Instead:

• Read the project structure.
• Read the debug report.
• Modify ONLY the files that require changes.

Return ONLY changed files.

Use this format exactly:

FILE: path/to/file.py
<new file content>

FILE: another/file.py
<content>

--------------------------------

PROJECT STRUCTURE

{project_structure}

--------------------------------

DEBUG REPORT

{debug_report}

--------------------------------

ORIGINAL TASK

{task}

"""

        return await LLMRouter.get_llm().generate(prompt)