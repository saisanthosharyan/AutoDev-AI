from app.services.execution.execution_manager import ExecutionManager

manager = ExecutionManager()

result = manager.run(
    "generated_projects/hello_world_python_program_implementation_plan_20260716_193730"
)

print(result)