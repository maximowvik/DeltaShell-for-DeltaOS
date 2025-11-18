import os


def clear_cmd():
    """Clear the terminal screen."""
    try:
        os.system("cls" if os.name == "nt" else "clear")
    except:
        print("\033[H\033[J", end="")
