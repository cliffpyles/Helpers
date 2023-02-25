import json


def get_parameters(args):
    parameters = []

    if args.parameters:
        for p in args.parameters:
            key, value = p.split("=")
            parameters.append({"ParameterKey": key, "ParameterValue": value})
    elif args.parameters_file:
        with open(args.parameters_file, "r") as f:
            parameters = json.load(f)

    return parameters
