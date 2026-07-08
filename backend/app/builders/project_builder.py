import os
import re
from pathlib import Path


class ProjectBuilder:

    def __init__(self):
        self.output_dir = Path("generated_projects")
        self.output_dir.mkdir(exist_ok=True)

    def build(self, project_name: str, llm_output: str):

        project_path = self.output_dir / project_name
        project_path.mkdir(exist_ok=True)

        pattern = r"FILE:\s*(.*?)\n```.*?\n(.*?)```"

        matches = re.findall(pattern, llm_output, re.DOTALL)

        created_files = []

        for file_path, content in matches:

            file_path = file_path.strip()

            full_path = project_path / file_path

            full_path.parent.mkdir(parents=True, exist_ok=True)

            with open(full_path, "w", encoding="utf-8") as f:
                f.write(content.strip())

            created_files.append(str(full_path))

        return {
            "project_path": str(project_path),
            "files": created_files
        }