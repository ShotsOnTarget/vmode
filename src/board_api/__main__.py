import json
import sys

from board_api.board_api import board_api


def main() -> None:
    hours = sys.argv[1] if len(sys.argv) > 1 else 0
    for question in board_api("open_questions", {"hours": hours}, {}):
        print(json.dumps(question))


if __name__ == "__main__":
    main()
