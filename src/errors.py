class MissingEnvVariable(Exception):
    def __init__(self, var_name: str) -> None:
        super().__init__(f"Missing environment variable: {var_name}")
