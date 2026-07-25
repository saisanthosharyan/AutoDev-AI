from app.agents.base_agent import BaseAgent
from app.core.logger import logger
from app.services.llm.router import LLMRouter


class ReviewerAgent(BaseAgent):
    """
    Reviews the generated project and provides actionable feedback
    on correctness, maintainability, security, and production readiness.
    """

    async def run(
        self,
        code: str,
    ) -> str:

        logger.info("=" * 60)
        logger.info("Reviewer Agent Started")
        logger.info("=" * 60)

        llm = LLMRouter.get_llm()

        prompt = f"""
You are a Principal Software Architect performing a production-grade code review.

Your objective is to review the ENTIRE generated project and identify every issue
that could affect quality, correctness, security, scalability or deployment.

==================================================
PROJECT SOURCE CODE
==================================================

{code}

==================================================
REVIEW CHECKLIST
==================================================

Review the project for:

• Architecture
• Folder structure
• Naming conventions
• Readability
• Maintainability
• Code duplication
• Runtime bugs
• Syntax issues
• Missing files
• Missing dependencies
• Import problems
• API correctness
• Database design
• Authentication
• Authorization
• Logging
• Exception handling
• Configuration
• Environment variables
• Docker support
• Test coverage
• Security vulnerabilities
• Performance bottlenecks
• Scalability

==================================================
OUTPUT FORMAT
==================================================

## Overall Summary

Provide a short summary.

---

## Strengths

List the project's strengths.

---

## Problems Found

For every issue include:

- File
- Problem
- Reason
- Severity (Low / Medium / High)

---

## Possible Runtime Errors

List all possible runtime failures.

---

## Security Review

Check for:

- Hardcoded secrets
- SQL Injection
- XSS
- CSRF
- Command Injection
- Unsafe subprocess usage
- File upload vulnerabilities
- Authentication issues
- Authorization issues
- Sensitive data exposure

---

## Performance Review

Mention:

- Slow algorithms
- Duplicate processing
- Memory issues
- Blocking operations
- Expensive API calls

---

## Code Quality

Review:

- SOLID principles
- DRY principles
- Clean Architecture
- Modularization
- Naming
- Documentation

---

## Missing Files

Mention missing files such as:

README.md

requirements.txt

package.json

Dockerfile

docker-compose.yml

.env.example

tests

GitHub Actions

CI/CD

LICENSE

---

## Final Suggestions

Provide concrete improvements that can be applied automatically.

---

## Final Score

Give a score out of 10.

==================================================
RULES
==================================================

- Do NOT rewrite the project.
- Do NOT generate source code.
- Be specific.
- Focus on actionable improvements.
- Mention both strengths and weaknesses.
- Prefer production-readiness over style opinions.
"""

        logger.info("Reviewing generated project...")

        review = await llm.generate(prompt)

        logger.info("Review completed successfully.")

        logger.info("=" * 60)
        logger.info("Reviewer Agent Finished")
        logger.info("=" * 60)

        return review