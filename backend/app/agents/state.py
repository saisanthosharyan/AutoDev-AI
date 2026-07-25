from dataclasses import dataclass, field
from typing import Any


@dataclass
class AgentState:
    """
    Shared state used by all AutoDev-AI agents.
    """

    # -------------------------
    # User Input
    # -------------------------

    prompt: str = ""

    # -------------------------
    # Planner
    # -------------------------

    plan: str = ""

    # -------------------------
    # Code Generation
    # -------------------------

    code: str = ""

    project: dict = field(default_factory=dict)

    # -------------------------
    # Review
    # -------------------------

    review: str = ""

    # -------------------------
    # Execution
    # -------------------------

    execution: dict = field(default_factory=dict)

    # -------------------------
    # Debugging
    # -------------------------

    debug_report: str = ""

    # -------------------------
    # Evaluation
    # -------------------------

    evaluation: dict = field(default_factory=dict)

    score: int = 0

    # -------------------------
    # Retry Information
    # -------------------------

    retry_count: int = 0

    max_retries: int = 3

    # -------------------------
    # Completion
    # -------------------------

    success: bool = False

    # -------------------------
    # Metadata
    # -------------------------

    metadata: dict[str, Any] = field(default_factory=dict)