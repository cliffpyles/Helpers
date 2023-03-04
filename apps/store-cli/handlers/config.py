from utils import save_config, restore_default_config


# Config Handlers

def get_config(args, config):
    print(config[args.key])


def set_config(args, config):
    config[args.key] = args.value
    save_config(config)
    print(f"Set {args.key} to {args.value}")


def delete_config(args, config):
    del config[args.key]
    save_config(config)
    print(f"Deleted {args.key}")


def list_config(args, config):
    print("Configuration:")
    for key, value in config.items():
        print(f"{key}: {value}")


def reset_config(args, config):
    restore_default_config()

