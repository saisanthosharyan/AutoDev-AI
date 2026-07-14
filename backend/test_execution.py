from app.services.execution.execution_manager import ExecutionManager

manager = ExecutionManager()

result = manager.run("generated_projects/sample_project")

print(result)