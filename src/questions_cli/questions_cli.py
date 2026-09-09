import json
import sys

from board_api.board_api import board_api


def questions_cli(argv: list[str]) -> int:
    """Print every open question the board reports, one JSON line each.

    Takes argv, the command-line arguments after the program name, and
    reads argv[0] as the hours window to hand to board_api, or 0 when
    absent. Prints one json.dumps(question) per line for every question
    in board_api("open_questions", {"hours": hours}, {}) and returns 0.
    """
    hours = argv[0] if argv else 0
    for question in board_api("open_questions", {"hours": hours}, {}):
        print(json.dumps(question))
    return 0


if __name__ == "__main__":
    sys.exit(questions_cli(sys.argv[1:]))
