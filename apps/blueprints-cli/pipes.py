def capitalize(value):
    return value.capitalize()


def upper(value):
    return value.upper()


def lower(value):
    return value.lower()


def kebab_case(value):
    return value.replace(" ", "-").lower()


def snake_case(value):
    return value.replace(" ", "_").lower()


def camel_case(value):
    words = value.split(" ")
    return words[0].lower() + "".join(word.capitalize() for word in words[1:])
