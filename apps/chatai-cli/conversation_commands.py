import sys

def exit_command(app_state):
    sys.exit()

def enable_multiline_command(app_state):
    app_state["multiline_mode"] = True

    return app_state

conversation_commands = {
    "exit": exit_command,
    "multi": enable_multiline_command
}