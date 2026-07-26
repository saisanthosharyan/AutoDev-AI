from app.core.logger import logger
from app.services.debugger.error_analyzer import ErrorAnalyzer


class DebugManager:
    """
    Converts execution results into a structured debugging report.

    The report is passed to the FixerAgent so the LLM can understand
    what failed and repair the generated project.
    """

    def __init__(self):

        self.error_analyzer = ErrorAnalyzer()

    # ==========================================================
    # ANALYZE
    # ==========================================================

    def analyze(
        self,
        execution_result: dict | None,
    ) -> dict:

        logger.info("=" * 60)
        logger.info("Debug Manager Started")
        logger.info("=" * 60)

        # ======================================================
        # No execution result
        # ======================================================

        if execution_result is None:

            logger.warning(
                "Execution result is None."
            )

            report = {
                "error": "Execution never started.",

                "root_cause": (
                    "The execution system did not return "
                    "an execution result."
                ),

                "solution": (
                    "Verify project generation, project structure, "
                    "entry point, and executor configuration."
                ),

                "category": "ExecutionError",

                "summary": (
                    "Execution never started."
                ),

                "recommendation": (
                    "Verify project structure and executor configuration."
                ),

                "stdout": "",

                "stderr": (
                    "Execution never started."
                ),

                "return_code": -1,
            }

            self._finish_log()

            return report

        # ======================================================
        # Successful execution
        # ======================================================

        if execution_result.get("success"):

            logger.info(
                "Project executed successfully."
            )

            report = {
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

            self._finish_log()

            return report

        # ======================================================
        # Error analysis
        # ======================================================

        try:

            analysis = self.error_analyzer.analyze(
                execution_result
            )

        except Exception as e:

            logger.exception(
                "Error Analyzer crashed."
            )

            stderr = execution_result.get(
                "stderr",
                "",
            )

            report = {
                "error": stderr or str(e),

                "root_cause": (
                    "The error analyzer could not determine "
                    "the exact root cause."
                ),

                "solution": (
                    "Inspect the execution logs and repair "
                    "the failing project."
                ),

                "category": "UnknownError",

                "summary": "Execution failed.",

                "recommendation": (
                    "Inspect stdout, stderr, and return code."
                ),

                "stdout": execution_result.get(
                    "stdout",
                    "",
                ),

                "stderr": stderr or str(e),

                "return_code": execution_result.get(
                    "return_code",
                    -1,
                ),
            }

            self._finish_log()

            return report

        # ======================================================
        # Extract analyzer data
        # ======================================================

        stdout = analysis.get(
            "stdout",
            execution_result.get(
                "stdout",
                "",
            ),
        )

        stderr = analysis.get(
            "stderr",
            execution_result.get(
                "stderr",
                "",
            ),
        )

        return_code = analysis.get(
            "return_code",
            execution_result.get(
                "return_code",
                -1,
            ),
        )

        category = analysis.get(
            "category",
            "UnknownError",
        )

        summary = analysis.get(
            "summary",
            "Execution failed.",
        )

        recommendation = analysis.get(
            "recommendation",
            (
                "Inspect the execution error and "
                "repair the project."
            ),
        )

        # ======================================================
        # Structured report
        # ======================================================

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
            f"Debug category: {category}"
        )

        logger.info(
            "Debug report generated successfully."
        )

        self._finish_log()

        return report

    # ==========================================================
    # LOGGING
    # ==========================================================

    def _finish_log(self):

        logger.info("=" * 60)
        logger.info("Debug Manager Finished")
        logger.info("=" * 60)