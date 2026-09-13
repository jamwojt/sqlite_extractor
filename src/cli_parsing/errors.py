

class MissingCLIArgument(Exception):
    def __init__(self, arg_name):
        super().__init__(f"Missing CLI argument: {arg_name}")
