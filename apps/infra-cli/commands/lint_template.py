import subprocess


def lint_template(template_file):
    try:
        result = subprocess.run(['cfn-lint', template_file], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if result.returncode == 0:
            print("No linting issues found!")
        else:
            print(f"{result.stdout.decode().strip()}")
    except FileNotFoundError:
        print("cfn-lint is not installed or not in your system path.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
