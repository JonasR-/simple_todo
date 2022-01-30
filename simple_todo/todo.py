import pathlib
import datetime
from typing import Callable

import yaml

import connectors

PROJECT_DIR = pathlib.Path(__file__).parent.parent
CONFIG_PATH = PROJECT_DIR.joinpath('config.yml')

PROMPT_CHARS = ">> "

menu_entries = []


def register_menu_entry(position: int, label: str) -> Callable:
    # used to register new menu entries and save them with position and label in `menu_entries`

    def decorator(function):
        menu_entries.append((function, position, label))

        def wrapper(*args, **kwargs):
            function(*args, **kwargs)
        return wrapper
    return decorator


def check_is_valid_date(date: str) -> bool:
    try:
        datetime.date.fromisoformat(date)
    except ValueError:
        return False
    return True


@register_menu_entry(99, "Exit")
def quit_program(connector: connectors.Connector):
    raise KeyboardInterrupt


@register_menu_entry(2, "Add Todo")
def show_add_todo_menu(connector: connectors.Connector):
    print("Input your todo text")
    todo_text = get_user_input(multiline_allowed=True)
    print("Enter a due date (yyyy-mm-dd)")
    due_date_text = get_user_input(validate_function=check_is_valid_date)

    connector.add_todo(todo_text, due_date_text)


@register_menu_entry(1, "Show Todo`s")
def show_todos(connector: connectors.Connector):
    for entry in connector.list_todos():
        print(f"{entry[2]}: {entry[1]}")


def get_user_input(
        possible_inputs: list | tuple = None,
        multiline_allowed: bool = False,
        validate_function: Callable[[str], bool] = None
) -> str:
    line_buffer = []

    while True:
        user_input = input(PROMPT_CHARS).strip()

        if possible_inputs and user_input not in possible_inputs:
            # if the user did not input the expected possible inputs, ask again for an input
            continue
        elif multiline_allowed and not user_input and line_buffer and not line_buffer[-1]:
            # if the user is allowed to input more than one line
            # and inputs two empty lines in a row, the input is complete
            break
        elif validate_function:
            # check the user input with the provided validator function
            if not validate_function(user_input):
                continue

        # add user input to buffer list
        line_buffer.append(user_input)

        if not multiline_allowed:
            # if we want only one input from the user break the loop and return
            break
    return "\n".join(line_buffer)


def handle_main_menu(connector: connectors.Connector):
    # sort menu entries by the position they registered at.
    sorted_menu_entries = sorted(menu_entries, key=lambda e: e[1])

    possible_inputs = []
    for index, entry in enumerate(sorted_menu_entries):
        index += 1
        # save index of the menu entry for user input validation
        possible_inputs.append(str(index))
        # print menu entry and index
        print(f"{index}. {entry[2]}")

    input_menu_id = get_user_input(possible_inputs=possible_inputs)

    # call the menu, chosen by the user and pass the connector to it
    sorted_menu_entries[int(input_menu_id) - 1][0](connector)


def read_config():
    with open(CONFIG_PATH) as fh:
        return yaml.load(fh, yaml.CLoader)


def main():
    config = read_config()

    # get the connector which stores the todos
    connector = connectors.connectors[config["connector"]["name"]](*config["connector"]["parameter"])

    # loop forever through the main menu
    while True:
        try:
            handle_main_menu(connector)
        except KeyboardInterrupt:
            break


if __name__ == '__main__':
    main()
