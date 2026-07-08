from app.services.llm.router import LLMRouter
from app.agents.base_agent import BaseAgent
from app.models.task import Task


class CoderAgent(BaseAgent):

    async def run(self, task: Task):

        llm = LLMRouter.get_llm()

        steps = "\n".join(
            f"- {step}" for step in task.steps
        )

        prompt = f"""
You are an Expert Software Engineer.

Your task is to generate an ENTIRE production-ready software project.

Project Title:
{task.title}

Project Description:
{task.description}

Implementation Steps:
{steps}

Follow every step carefully.

Return ONLY project files.

Rules:

- Every file MUST begin exactly like:

FILE: path/to/file.py

<file contents>

- Do NOT wrap files inside markdown.

- Do NOT use ```.

- Do NOT explain anything.

- Do NOT summarize.

- Return ALL necessary files.

Include at minimum:

README.md
requirements.txt (or package.json)
.gitignore
configuration files
source code
tests
Dockerfile (if applicable)

Generate COMPLETE code.

Never skip files.

Never say "Here is your project."

Output ONLY files.
"""

        print("=" * 80)
        print("CODER PROMPT")
        print("=" * 80)
        print(prompt)
        print("=" * 80)

        response = await llm.generate(prompt)

        print("=" * 80)
        print("CODER RESPONSE LENGTH:", len(response))
        print("=" * 80)

        return response