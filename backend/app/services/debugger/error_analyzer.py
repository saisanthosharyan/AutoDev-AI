from app.core.logger import logger


class ErrorAnalyzer:
    """
    Performs lightweight analysis of execution errors before
    sending them to the AI Fixer Agent.
    """

    ERROR_PATTERNS = {
        "ModuleNotFoundError": "Missing Python module or dependency.",
        "ImportError": "Import statement failed.",
        "SyntaxError": "Python syntax error.",
        "IndentationError": "Indentation issue.",
        "NameError": "Undefined variable or function.",
        "TypeError": "Invalid object type usage.",
        "ValueError": "Invalid value supplied.",
        "AttributeError": "Object attribute does not exist.",
        "KeyError": "Dictionary key missing.",
        "IndexError": "List index out of range.",
        "FileNotFoundError": "Required file not found.",
        "PermissionError": "Permission denied.",
        "RuntimeError": "Runtime failure.",
        "TimeoutExpired": "Execution timeout.",
        "ConnectionError": "Network connection failed.",
        "JSONDecodeError": "Invalid JSON.",
    }

    def analyze(self, execution_result: dict | None) -> dict:
        """
        Returns a structured error analysis.

        {
            "category": "...",
            "summary": "...",
            "recommendation": "...",
            "stderr": "...",
            "stdout": "...",
            "return_code": -1
        }
        """

        logger.info("Running Error Analyzer...")

        if execution_result is None:

            return {
                "category": "Unknown",
                "summary": "Execution never started.",
                "recommendation": "Verify project generation and execution pipeline.",
                "stdout": "",
                "stderr": "",
                "return_code": -1,
            }

        stdout = execution_result.get("stdout") or ""
        stderr = execution_result.get("stderr") or ""
        return_code = execution_result.get("return_code", -1)

        combined = f"{stdout}\n{stderr}"

        category = "Unknown Error"
        summary = "Unable to determine failure reason."

        for error_name, description in self.ERROR_PATTERNS.items():

            if error_name.lower() in combined.lower():

                category = error_name
                summary = description
                break

        recommendation = self._recommendation(category)

        logger.info(f"Detected Error: {category}")

        return {
            "category": category,
            "summary": summary,
            "recommendation": recommendation,
            "stdout": stdout,
            "stderr": stderr,
            "return_code": return_code,
        }

    def _recommendation(self, category: str) -> str:
        """
        Suggest a repair strategy.
        """

        recommendations = {
            "ModuleNotFoundError": "Install the missing package and update imports.",
            "ImportError": "Correct incorrect imports or missing modules.",
            "SyntaxError": "Fix syntax mistakes.",
            "IndentationError": "Correct indentation.",
            "NameError": "Define the missing variable or function.",
            "TypeError": "Check argument types and function signatures.",
            "ValueError": "Validate input values.",
            "AttributeError": "Verify object methods and attributes.",
            "KeyError": "Check dictionary keys before accessing them.",
            "IndexError": "Validate list indexes.",
            "FileNotFoundError": "Create the missing file or correct its path.",
            "PermissionError": "Check file or directory permissions.",
            "RuntimeError": "Inspect runtime logic.",
            "TimeoutExpired": "Optimize execution or increase timeout.",
            "ConnectionError": "Verify network connectivity and endpoints.",
            "JSONDecodeError": "Validate JSON format.",
        }

        return recommendations.get(
            category,
            "Inspect logs and repair the project automatically."
        )