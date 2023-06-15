import sys
from pathlib import Path
import pyperclip
import time
import datetime
import pytz
import shutil
import tzlocal
import yaml


def select_conversation_items(conversation, selector):
    conversation_items = None
    if not selector:
        return conversation_items
    elif selector == "last":
        conversation_items = conversation.last_item()
        return [conversation_items]
    elif selector == "all":
        conversation_items = conversation.get_items()
        return conversation_items
    elif selector == "all_responses":
        conversation_items = conversation.filter_items({"role": "assistant"})
        return conversation_items
    elif selector == "all_messages":
        conversation_items = conversation.filter_items({"role": "user"})
        return conversation_items
    elif ":" in selector:
        start, end = map(int, selector.split(":"))
        all_responses = conversation.get_items()
        conversation_items = all_responses[start - 1 : end + 1]
        return conversation_items
    elif selector.isdigit():
        all_responses = conversation.get_items()
        conversation_items = all_responses[int(selector) - 1]
        return conversation_items
    else:
        conversation_items = conversation.get_item(selector)
        return [conversation_items]


def attach_file_command(command_name, args, conversation, current_state, user_input):
    for filepath in args:
        file = Path(filepath).expanduser()
        file_content = file.read_text()
        conversation.add_item(
            {
                "role": "user",
                "name": current_state["username"],
                "content": file_content,
                "mac_address": current_state["mac_address"],
            }
        )

    return conversation, current_state, user_input


def copy_to_clipboard_command(
    command_name, args, conversation, current_state, user_input
):
    selector = args[0] if args else None
    selected_items = select_conversation_items(conversation, selector)

    if not selected_items:
        current_state["notifications"] = [f"no items found to copy"]
    else:
        content_to_copy = ""
        content_to_copy += "\n\n".join(
            [selected_item.get("content") for selected_item in selected_items]
        ).strip()
        current_state["notifications"] = ["copied successfully"]
        if len(content_to_copy) > 0:
            pyperclip.copy(content_to_copy)

    return conversation, current_state, user_input


def enable_multiline_command(
    command_name, args, conversation, current_state, user_input
):
    current_state["multiline_mode"] = True

    return conversation, current_state, user_input


def export_command(command_name, args, conversation, current_state, user_input):
    def save_prompt(filepath, prompt):
        def str_presenter(dumper, data):
            if len(data.splitlines()) > 1:  # check for multiline string
                return dumper.represent_scalar("tag:yaml.org,2002:str", data, style="|")
            return dumper.represent_scalar("tag:yaml.org,2002:str", data)

        yaml.add_representer(str, str_presenter)
        yaml.representer.SafeRepresenter.add_representer(str, str_presenter)
        filepath = Path(filepath).expanduser()
        content = yaml.dump(prompt, default_flow_style=False, sort_keys=False)
        filepath.write_text(content, newline=None)
        return filepath

    filepath = Path(args[0]).expanduser()
    model = current_state.get("model", "gpt-3.5-turbo")

    if not filepath.is_file():
        messages = conversation.get_items(fields=["role", "name", "content"])
        prompt = {"model": model, "messages": messages}
        save_prompt(filepath, prompt)
        current_state["notifications"] = [f"exported to {args[0]}"]
    else:
        current_state["notifications"] = [f"{args[0]} already exists"]

    return conversation, current_state, user_input


def exit_command(command_name, args, conversation, current_state, user_input):
    sys.exit()


def remove_message_command(command_name, args, conversation, current_state, user_input):
    selector = args[0] if args else None
    selected_items = select_conversation_items(conversation, selector)

    if not selected_items:
        current_state["notifications"] = [f"no items found to remove"]
    else:
        for selected_item in selected_items:
            conversation.remove_item(selected_item.get("id"))

    return conversation, current_state, user_input


def send_command(command_name, args, conversation, current_state, user_input):
    current_state["send_messages"] = True

    return conversation, current_state, user_input


def snapshot_command(command_name, args, conversation, current_state, user_input):
    def timestamp_to_human(timestamp, timezone):
        dt = datetime.datetime.fromtimestamp(timestamp, pytz.timezone(timezone))

        return dt.strftime("%B %d, %Y %H:%M:%S %Z")

    def create_snapshot():
        current_timestamp = int(time.time())
        conversation_file_path = Path(conversation.file_name)
        snapshot_path = conversation_file_path.with_suffix(
            f".{current_timestamp}.snapshot"
        )
        shutil.copyfile(str(conversation_file_path), str(snapshot_path))

        current_state["notifications"] = [f"snapshot created: {snapshot_path.stem}"]

    def list_snapshots():
        conversation_file_path = Path(conversation.file_name)
        snapshots = conversation_file_path.parent.glob(
            f"{conversation_file_path.stem}.*.snapshot"
        )
        current_timezone = tzlocal.get_localzone()
        current_state["notifications"] = []
        for snapshot in snapshots:
            timestamp = snapshot.suffixes[-2][1:]
            formatted_timestamp = timestamp_to_human(int(timestamp), "America/New_York")
            current_state["notifications"].append(
                f"{snapshot.stem} ({formatted_timestamp})\n"
            )

    def rollback_to_snapshot():
        snapshot_name = "latest" if len(args) < 2 else args[1]
        conversation_file_path = Path(conversation.file_name)
        snapshots = conversation_file_path.parent.glob(
            f"{conversation_file_path.stem}.*.snapshot"
        )
        selected_snapshot = None
        snapshots = list(snapshots)
        if snapshot_name == "latest" and snapshots > 0:
            selected_snapshot = snapshots[-1]
        elif len(snapshots) > 0:
            for snapshot in snapshots:
                if snapshot.stem == snapshot_name:
                    selected_snapshot = snapshot
                    break

        if selected_snapshot:
            shutil.copyfile(str(selected_snapshot), str(conversation_file_path))
            current_state["notifications"] = [
                f"Rollback to {selected_snapshot.stem} complete"
            ]
        else:
            current_state["notifications"] = ["No matching rollbacks found"]

    def delete_snapshot():
        snapshot_name = "latest" if len(args) < 2 else args[1]
        conversation_file_path = Path(conversation.file_name)
        snapshots = conversation_file_path.parent.glob(
            f"{conversation_file_path.stem}.*.snapshot"
        )
        selected_snapshot = None
        snapshots = list(snapshots)
        if snapshot_name == "latest" and snapshots > 0:
            selected_snapshot = snapshots[-1]
        elif len(snapshots) > 0:
            for snapshot in snapshots:
                if snapshot.stem == snapshot_name:
                    selected_snapshot = snapshot
                    break

        if selected_snapshot:
            selected_snapshot.unlink()
            current_state["notifications"] = [
                f"Rollback {selected_snapshot.stem} deleted"
            ]
        else:
            current_state["notifications"] = ["No matching rollbacks found"]

    subcommands = {
        "create": create_snapshot,
        "list": list_snapshots,
        "rollback": rollback_to_snapshot,
        "delete": delete_snapshot,
    }

    subcommand_name = "list" if len(args) < 1 else args[0]
    subcommand = subcommands.get(subcommand_name, subcommands["list"])
    subcommand()

    return conversation, current_state, user_input


def unknown_command(command_name, args, conversation, current_state, user_input):
    current_state["warnings"] = [f"{command_name} is not a recognized command"]

    return conversation, current_state, user_input


conversation_commands = {
    "attach": attach_file_command,
    "copy": copy_to_clipboard_command,
    "delete": remove_message_command,
    "exit": exit_command,
    "export": export_command,
    "multi": enable_multiline_command,
    "remove": remove_message_command,
    "send": send_command,
    "snapshot": snapshot_command,
    "snapshots": snapshot_command,
    "unknown": unknown_command,
}


def attach_file_autocomplete(conversation):
    return None


def copy_to_clipboard_autocomplete(conversation):
    message_ids = [message.get("id") for message in conversation.get_items()]
    message_ids.sort()
    available_selectors = ["all", "all_messages", "all_responses", "last"]
    return set(available_selectors + message_ids)


def exit_autocomplete(conversation):
    return None


def export_autocomplete(conversation):
    return None


def enable_multiline_autocomplete(conversation):
    return None


def remove_message_autocomplete(conversation):
    message_ids = [message.get("id") for message in conversation.get_items()]
    message_ids.sort()
    available_selectors = ["all", "all_messages", "all_responses", "last"]
    return set(available_selectors + message_ids)


def send_autocomplete(conversation):
    return None


def snapshot_autocomplete(conversation):
    conversation_file_path = Path(conversation.file_name)
    snapshot_files = conversation_file_path.parent.glob(
        f"{conversation_file_path.stem}.*.snapshot"
    )
    snapshots = []
    for snapshot_file in snapshot_files:
        snapshots.append(snapshot_file.stem)

    return {
        "create": None,
        "list": None,
        "rollback": set(snapshots),
        "delete": set(snapshots),
    }


conversation_command_autocompletes = {
    "attach": attach_file_autocomplete,
    "copy": copy_to_clipboard_autocomplete,
    "delete": remove_message_autocomplete,
    "exit": exit_autocomplete,
    "export": export_autocomplete,
    "multi": enable_multiline_autocomplete,
    "remove": remove_message_autocomplete,
    "send": send_autocomplete,
    "snapshot": snapshot_autocomplete,
    "snapshots": snapshot_autocomplete,
}
