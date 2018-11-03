import traceback
import os
from termcolor import colored
import sys
import requests
import json
import html
from languages import lang_to_code


API_KEY = "AIzaSyA-e4wLSu-is3uq-QFCqu0lGIx6e8IrlC8"

def translate(s, language):
    if not language:
        return s
    else:
        payload = {'q': s, 'target': language, 'key': API_KEY}
        r = requests.post("https://translation.googleapis.com/language/translate/v2", params=payload)
        return html.unescape(json.loads(r.text)["data"]["translations"][0]["translatedText"])


def insert_error(line, error, filename):
    f = open(filename, "r")
    contents = f.readlines()
    f.close()

    contents.insert(line, "\"\"\"\n" + error + "\n\"\"\"\n")

    f = open(filename, "w")
    contents = "".join(contents)
    f.write(contents)
    f.close()


def static_analysis(filename, language=None):
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
            error = translate(' '.join(line[2:]), language)
            print("line: " + str(error_line) + ", " + colored("error: ", 'red') + str(error))
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
    if len(sys.argv) > 2:
        language = lang_to_code(sys.argv[2])
        if language == "not found":
            print("Language not found")
        else:
            static_analysis(filename, language=language)
    else:
        static_analysis(filename)
