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
You are a Principal Software Engineer and Software Architect.

Your job is to repair a generated software project.

The repaired project MUST compile, execute successfully, and preserve all existing functionality.

==================================================
GENERATED PROJECT
==================================================

{code}

==================================================
CODE REVIEW
==================================================

{review}

==================================================
EXECUTION ERRORS
==================================================

{execution_error}

Your responsibilities:

1. Fix all syntax errors.
2. Fix runtime errors.
3. Fix import errors.
4. Fix dependency issues.
5. Fix incorrect package versions.
6. Fix missing modules.
7. Fix broken APIs.
8. Fix database issues.
9. Fix configuration issues.
10. Fix Docker/configuration files if necessary.
11. Fix folder structure.
12. Add missing files if required.
13. Remove duplicate code.
14. Improve readability.
15. Improve performance where appropriate.
16. Preserve all working functionality.
17. Do NOT remove existing features.
18. Keep project architecture clean.
19. Ensure every generated file is complete.
20. Ensure the project is production-ready.

IMPORTANT OUTPUT RULES

Return ONLY project files.

Every file MUST begin exactly like this:

FILE: path/to/file.py

<file contents>

Do NOT use markdown.

Do NOT use ```.

Do NOT explain anything.

Do NOT summarize.

Do NOT say "Here is the fixed project."

Return the COMPLETE corrected project.

Every file should be included again, even if unchanged.

Output ONLY files.
"""

        logger.info("Starting AI project repair...")

        response = await llm.generate(prompt)

        logger.info("Project repair completed successfully.")

        return response