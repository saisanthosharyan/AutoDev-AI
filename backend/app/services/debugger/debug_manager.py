from app.core.logger import logger
from app.services.debugger.error_analyzer import ErrorAnalyzer


class DebugManager:
    """
    Builds a structured debugging report from execution results.

    Output format:
    {
        "error": str,
        "root_cause": str,
        "solution": str,
        "category": str,
        "summary": str,
        "recommendation": str,
        "stdout": str,
        "stderr": str,
        "return_code": int,
    }
    """

    def __init__(self):
        self.error_analyzer = ErrorAnalyzer()

    def analyze(self, execution_result: dict | None) -> dict:

        logger.info("=" * 60)
        logger.info("Debug Manager Started")
        logger.info("=" * 60)

        # --------------------------------------------------
        # No execution result
        # --------------------------------------------------

        if execution_result is None:

            logger.warning(
                "Execution result is None."
            )

            report = {
                "error": "Execution never started.",
                "root_cause": (
                    "The project execution process did not produce "
                    "an execution result."
                ),
                "solution": (
                    "Check the project structure, entry point, "
                    "executor configuration, and build process."
                ),
                "category": "execution",
                "summary": "Execution never started.",
                "recommendation": (
                    "Verify project structure and executor configuration."
                ),
                "stdout": "",
                "stderr": "Execution never started.",
                "return_code": -1,
            }

            logger.info(
                "Debug report generated."
            )

            logger.info("=" * 60)
            logger.info("Debug Manager Finished")
            logger.info("=" * 60)

            return report

        # --------------------------------------------------
        # Successful execution
        # --------------------------------------------------

        if execution_result.get("success"):

            logger.info(
                "Project executed successfully."
            )

            return {
                "error": "",
                "root_cause": "",
                "solution": "",
                "category": "success",
                "summary": "Project executed successfully.",
                "recommendation": "",
                "stdout": execution_result.get(
                    "stdout",
                    "",
                ),
                "stderr": execution_result.get(
                    "stderr",
                    "",
                ),
                "return_code": execution_result.get(
                    "return_code",
                    0,
                ),
            }

        # --------------------------------------------------
        # Analyze failed execution
        # --------------------------------------------------

        try:

            analysis = self.error_analyzer.analyze(
                execution_result
            )

        except Exception as e:

            logger.exception(
                "Error analyzer failed."
            )

            fallback = {
                "error": execution_result.get(
                    "stderr",
                    "Unknown execution error.",
                ),
                "root_cause": (
                    "The error analyzer could not determine "
                    "the root cause."
                ),
                "solution": (
                    "Inspect the execution stderr and return code "
                    "and repair the failing project."
                ),
                "category": "unknown",
                "summary": "Execution failed.",
                "recommendation": (
                    "Inspect stdout, stderr, and return code."
                ),
                "stdout": execution_result.get(
                    "stdout",
                    "",
                ),
                "stderr": execution_result.get(
                    "stderr",
                    str(e),
                ),
                "return_code": execution_result.get(
                    "return_code",
                    -1,
                ),
            }

            logger.info(
                "Fallback debug report generated."
            )

            return fallback

        # --------------------------------------------------
        # Safely extract analyzer values
        # --------------------------------------------------

        stdout = analysis.get(
            "stdout",
            execution_result.get("stdout", ""),
        )

        stderr = analysis.get(
            "stderr",
            execution_result.get("stderr", ""),
        )

        return_code = analysis.get(
            "return_code",
            execution_result.get("return_code", -1),
        )

        category = analysis.get(
            "category",
            "unknown",
        )

        summary = analysis.get(
            "summary",
            "Execution failed.",
        )

        recommendation = analysis.get(
            "recommendation",
            "Inspect the execution error and repair the project.",
        )

        # --------------------------------------------------
        # Create structured debug report
        # --------------------------------------------------

        report = {
            "error": stderr or summary,
            "root_cause": summary,
            "solution": recommendation,
            "category": category,
            "summary": summary,
            "recommendation": recommendation,
            "stdout": stdout,
            "stderr": stderr,
            "return_code": return_code,
        }

        logger.info(
            "Debug report generated."
        )

        logger.info("=" * 60)
        logger.info("Debug Manager Finished")
        logger.info("=" * 60)

        return report