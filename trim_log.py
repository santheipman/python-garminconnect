import os


def trim_file(file, num_lines):
    with open(file, 'r') as infile:
        lines = infile.readlines()

    with open(file, 'w') as outfile:
        outfile.writelines(lines[-num_lines:])


path = os.path.join(os.getenv("GARSYNC_SCRIPT_PATH"), os.getenv("GARSYNC_LOG_FILE"))
trim_file(path, 2000)

