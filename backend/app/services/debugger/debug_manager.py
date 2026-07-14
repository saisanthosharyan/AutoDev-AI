from app.core.logger import logger


class DebugManager:

    def analyze(self, execution_result: dict) -> dict:
        """
        Analyze execution results and determine whether the generated
        project needs to be fixed.
        """

        success = execution_result.get("success", False)
        stderr = execution_result.get("stderr", "")
        stdout = execution_result.get("stdout", "")

        if success:
            return {
                "needs_fix": False,
                "error": "",
                "reason": "Execution completed successfully."
            }

        logger.warning("Execution failed.")
        logger.warning(stderr)

        return {
            "needs_fix": True,
            "error": stderr,
            "stdout": stdout,
            "reason": "Runtime execution failed."
        }

    def create_fix_prompt(
        self,
        code: str,
        execution_result: dict,
    ) -> str:
        """
        Build a prompt for the FixerAgent.
        """

        return f"""
The generated project failed during execution.

Execution Error:

{execution_result.get("stderr", "")}

Execution Output:

{execution_result.get("stdout", "")}

Generated Code:

{code}

Fix ONLY the necessary files.

Do not rewrite the whole project.

Return the corrected project.
"""