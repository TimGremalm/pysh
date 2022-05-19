from pysh.tools import get_terminal_cursor_position, set_terminal_cursor_position
from rich.console import Console
from rich.table import Table


def printing(pysh):
    console = Console()
    pos = get_terminal_cursor_position()
    pos = 1, 1
    set_terminal_cursor_position(pos[0], pos[1])
    table = Table()
    table.add_column("Name")
    table.add_column("Value")
    table.add_row("console.width", str(console.width))
    table.add_row("console.height", str(console.height))
    # print(f"{console.width} {console.height}")
    console.print(table)
    set_terminal_cursor_position(1, console.height-1)
