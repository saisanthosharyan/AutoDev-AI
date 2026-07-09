class ExecutionResult:
    def __init__(
        self,
        success: bool,
        stdout: str,
        stderr: str,
        return_code: int,
    ):
        self.success = success
        self.stdout = stdout
        self.stderr = stderr
        self.return_code = return_code