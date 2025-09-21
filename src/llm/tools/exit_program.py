from src.exceptions import ExitProgramException
from pydantic_ai import RunContext


def exit_program(ctx: RunContext) -> str:
    raise ExitProgramException
