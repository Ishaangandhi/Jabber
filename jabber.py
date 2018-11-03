import traceback
import os
from termcolor import colored
import sys


def insert_error(line, error, filename):
    f = open(filename, "r")
    contents = f.readlines()
    f.close()

    contents.insert(line, "\"\"\"\n" + error + "\n\"\"\"\n")

    f = open(filename, "w")
    contents = "".join(contents)
    f.write(contents)
    f.close()


def static_analysis(filename):
    print(colored("Running static analysis...", 'blue'))
    p = os.popen('flake8 --ignore E ' + filename).read()
    if p == "":
        print(colored("No errors found.", 'green'))
    else:
        p = p.splitlines()
        for i, line in enumerate(p):
            line = line.split()
            error_file = line[0].split(':')
            error_line = int(error_file[1])
            error = ' '.join(line[2:])
            print("line: " + str(error_line) + ", error: " + str(error))
            insert_error(error_line+3*i, error, filename)


def run_program():
    try:
        exec(open("test1.py").read())
        print(colored('No errors detected', 'green'))
    except Exception:
        var = traceback.format_exc()
        print(colored("var: ", 'red') + var)


if __name__ == "__main__":
    filename = sys.argv[1]
    static_analysis(filename)
