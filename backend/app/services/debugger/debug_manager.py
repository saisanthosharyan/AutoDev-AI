from app.core.logger import logger


class DebugManager:
    """
    Analyzes execution results and prepares an AI-friendly
    debugging report for the Fixer Agent.
    """

    def analyze(self, execution_result: dict | None) -> str:
        """
        Analyze execution results and return a debugging report.
        """

        logger.info(
            "Analyzing execution results..."
        )

        if execution_result is None:

            logger.warning(
                "Execution result is None."
            )

            return """
=========================
EXECUTION REPORT
=========================

Execution never started.

Please identify why execution did not begin
and fix all issues preventing startup.
"""

        if execution_result.get("success", False):

            logger.info(
                "No execution errors detected."
            )

            return ""

        stdout = execution_result.get(
            "stdout",
            "",
        )

        stderr = execution_result.get(
            "stderr",
            "",
        )

        return_code = execution_result.get(
            "return_code",
            -1,
        )

        report = f"""
=========================
EXECUTION REPORT
=========================

Status:
FAILED

Return Code:
{return_code}

-------------------------
STDOUT
-------------------------

{stdout}

-------------------------
STDERR
-------------------------

{stderr}

-------------------------
TASK
-------------------------

Identify every issue preventing execution.

Fix:

1. Syntax errors
2. Runtime errors
3. Import errors
4. Dependency issues
5. Missing files
6. Configuration problems

Return the fully corrected project.
"""

        logger.info(
            "Debug report generated."
        )

        return report