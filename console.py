from rich.console import Console

console = Console()

def move_cursor(row, column):
    print(f'\033[{row};{column}H', end='')
