from pysh.tools import get_terminal_cursor_position, set_terminal_cursor_position
from rich.console import Console


def printing(pysh):
    console = Console()
    pos = get_terminal_cursor_position()
    pos = 1, 1
    set_terminal_cursor_position(pos[0], pos[1])
    print(f"{console.width} {console.height}")
    set_terminal_cursor_position(1, console.height-1)
