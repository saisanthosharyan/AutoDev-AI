from app.services.llm.router import LLMRouter
from app.agents.base_agent import BaseAgent
from app.core.logger import logger


class ReviewerAgent(BaseAgent):

    async def run(
        self,
        code: str,
    ):

        llm = LLMRouter.get_llm()

        prompt = f"""
You are a Principal Software Engineer performing a production-ready code review.

Review the following generated project.

Your job is to identify every possible issue that could affect:

- correctness
- maintainability
- scalability
- readability
- security
- performance
- testing
- deployment

Provide your review using the following format.

## Overall Summary

Short summary of the project quality.

---

## Strengths

- ...

---

## Problems Found

For each issue include:

- File (if identifiable)
- Problem
- Why it is a problem
- Severity (Low/Medium/High)

---

## Possible Bugs

List runtime errors, syntax issues, logic bugs or missing implementations.

---

## Security Issues

Mention:

- secrets
- authentication
- authorization
- SQL Injection
- XSS
- CSRF
- unsafe file handling
- unsafe subprocess usage
- insecure API usage

---

## Performance Improvements

Mention slow algorithms, duplicate work, unnecessary API calls, memory issues etc.

---

## Code Quality Improvements

Mention:

- naming
- modularity
- comments
- duplicated code
- architecture

---

## Missing Files

Mention any important missing files like:

README.md

requirements.txt

package.json

Dockerfile

.env.example

tests

CI/CD configuration

---

## Final Suggestions

Provide concrete improvements the coding agent can apply during regeneration.

---

## Final Score

Score out of 10.

Project Code:

{code}

Rules:

- Be specific.
- Do not rewrite the entire project.
- Focus on actionable improvements.
"""

        logger.info("Reviewing generated project...")

        response = await llm.generate(prompt)

        logger.info("Reviewer completed successfully.")

        return response