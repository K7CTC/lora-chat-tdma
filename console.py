from rich.console import Console

console = Console()

def cursor_hide():
    print(f'\033[?25l', end='')
def cursor_show():
    print(f'\033[?25h', end='')
def cursor_move(row, column):
    print(f'\033[{row};{column}H', end='')
