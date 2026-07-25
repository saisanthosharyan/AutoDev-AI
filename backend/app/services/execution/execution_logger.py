import json
from pathlib import Path
from datetime import datetime


class ExecutionLogger:

    def __init__(self, project_path: str):
        self.project = Path(project_path)
        self.logs = self.project / "execution"
        self.logs.mkdir(parents=True, exist_ok=True)

    def save(self, result: dict):

        (self.logs / "stdout.txt").write_text(
            result.get("stdout", ""),
            encoding="utf-8",
        )

        (self.logs / "stderr.txt").write_text(
            result.get("stderr", ""),
            encoding="utf-8",
        )

        with open(
            self.logs / "execution.json",
            "w",
            encoding="utf-8",
        ) as f:

            json.dump(
                {
                    "timestamp": datetime.now().isoformat(),
                    **result,
                },
                f,
                indent=4,
            )

        with open(
            self.logs / "execution.log",
            "a",
            encoding="utf-8",
        ) as f:

            f.write("=" * 70 + "\n")
            f.write(datetime.now().isoformat() + "\n")
            f.write(f"Success : {result['success']}\n")
            f.write(f"Return Code : {result['return_code']}\n")
            f.write(
                f"Execution Time : {result['execution_time']} sec\n"
            )
            f.write("=" * 70 + "\n\n")