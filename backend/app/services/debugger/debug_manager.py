from app.core.logger import logger


class DebugManager:
    """
    Analyzes execution results and prepares an AI-friendly
    debugging report for the Fixer Agent.
    """

    def analyze(self, execution_result: dict) -> str:
        """
        Analyze execution results and return a debugging report.
        """

        logger.info("Analyzing execution results...")

        if execution_result.get("success", False):
            logger.info("No execution errors detected.")
            return ""

        stdout = execution_result.get("stdout", "")
        stderr = execution_result.get("stderr", "")
        return_code = execution_result.get("return_code", -1)

        report = f"""
Execution failed.

Return Code:
{return_code}

STDOUT:
{stdout}

STDERR:
{stderr}

Your task is to identify the cause of the failure and fix every issue
so the project can execute successfully.
"""

        logger.info("Debug report generated.")

        return report