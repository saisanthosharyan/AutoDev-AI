from app.core.logger import logger

from app.services.evaluator.project_checker import ProjectChecker
from app.services.evaluator.quality_checker import QualityChecker
from app.services.evaluator.documentation_checker import DocumentationChecker
from app.services.execution.execution_manager import ExecutionManager


class Evaluator:
    """
    Evaluates the generated project.

    Checks:

    1. Project Structure
    2. Execution
    3. Code Quality
    4. Documentation

    Produces a final score and recommendation.
    """

    def __init__(self):

        self.project_checker = ProjectChecker()
        self.quality_checker = QualityChecker()
        self.documentation_checker = DocumentationChecker()
        self.execution_manager = ExecutionManager()

    # --------------------------------------------------

    def evaluate(
        self,
        project_path: str,
    ) -> dict:

        logger.info("=" * 60)
        logger.info("Starting Project Evaluation")
        logger.info("=" * 60)

        # --------------------------------------------------
        # Detect Project Type
        # --------------------------------------------------

        project_type = self.execution_manager.detect_project_type(
            project_path
        )

        logger.info(
            f"Detected project type: {project_type}"
        )

        # --------------------------------------------------
        # Project Structure
        # --------------------------------------------------

        structure = self.project_checker.check(
            project_path,
            project_type,
        )

        # --------------------------------------------------
        # Execution
        # --------------------------------------------------

        execution = self.execution_manager.run(
            project_path
        )

        execution_score = (
            100
            if execution.get("success")
            else 0
        )

        # --------------------------------------------------
        # Quality
        # --------------------------------------------------

        quality = self.quality_checker.check(
            project_path
        )

        # --------------------------------------------------
        # Documentation
        # --------------------------------------------------

        documentation = (
            self.documentation_checker.check(
                project_path
            )
        )

        # --------------------------------------------------
        # Overall Score
        # --------------------------------------------------

        overall_score = round(

            (
                structure["score"]
                + execution_score
                + quality["score"]
                + documentation["score"]
            )

            / 4

        )

        # --------------------------------------------------
        # Recommendation
        # --------------------------------------------------

        if overall_score >= 90:

            recommendation = (
                "Excellent. Project is production ready."
            )

        elif overall_score >= 75:

            recommendation = (
                "Good project. Minor improvements recommended."
            )

        elif overall_score >= 60:

            recommendation = (
                "Average project. Needs improvements."
            )

        else:

            recommendation = (
                "Project requires major fixes."
            )

        logger.info(
            f"Overall Evaluation Score: {overall_score}"
        )

        logger.info(
            recommendation
        )

        logger.info("=" * 60)
        logger.info("Evaluation Completed")
        logger.info("=" * 60)

        return {

            "overall_score": overall_score,

            "recommendation": recommendation,

            "project_type": project_type,

            "structure": structure,

            "execution": execution,

            "quality": quality,

            "documentation": documentation,

        }