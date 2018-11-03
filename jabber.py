# encoding=utf8

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


def getStackOverflowAnswer(query):
    cse_url = "https://www.googleapis.com/customsearch/v1?cx=011944706024575323675:_py65c8dw6e&q=" + query + "&key=AIzaSyCh0MRGhTXwyAX270l_f6nIWZPVORgwibY"
    # Make a Google CSE Search
    results = requests.get(cse_url)
    firstResult = results.json()['items'][0]
    link = firstResult['link']
    splitLink = link.split("/")
    questionId = splitLink[4]

    stackOverFlowLink = "https://api.stackexchange.com/2.2/questions/" + questionId + "/answers?site=stackoverflow&key=RKKAKKosLuCpQGsWMoMVFw((&filter=withbody"
    # Stack Overflow Search
    stackResults = requests.get(stackOverFlowLink)
    bodyHtml = stackResults.json()["items"][0]["body"]

    if (bodyHtml == "" or bodyHtml is None):
        print("No Body Gotten! Here is google result:")
        print(str(results.json()).encode("utf-8"))
        print("Stack OverFlow:")
        print(str(stackResults.json()).encode("utf-8"))

    return bodyHtml

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
        line_numbers = []
        for i, line in enumerate(p):
            line = line.split()
            error_file = line[0].split(':')
            error_line = int(error_file[1])
            error = translate(' '.join(line[2:]), language)
            line_numbers.append(str(error_line+3*i))
            insert_error(error_line+3*i, error, filename)
        print(colored("error lines: ", 'red') + ' '.join(line_numbers))



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
