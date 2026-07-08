from app.services.llm.router import LLMRouter
from app.agents.base_agent import BaseAgent


"""class ReviewerAgent(BaseAgent):

    async def run(self, code: str):

        llm = LLMRouter.get_llm()

        prompt = f"""
"""You are a Senior Code Reviewer.

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

"""return await llm.generate(prompt)"""
class ReviewerAgent(BaseAgent):

    async def run(self, code: str):

        llm = LLMRouter.get_llm()

        prompt = f"""
You are a Senior Software Engineer performing a professional code review.

The following text contains an ENTIRE SOFTWARE PROJECT.

Each file begins with:

FILE: <filename>

Review ALL files, not just the first one.

Evaluate:

1. Architecture
2. Folder Structure
3. Code Quality
4. Best Practices
5. Security Issues
6. Performance
7. Bugs
8. Improvements
9. Final Score (/10)

Project:

{code}
"""