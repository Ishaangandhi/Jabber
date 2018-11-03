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
SESSION_ID = 1
APP_ENDPOINT = "https://jabber-5c.herokuapp.com/user_errors"

def translate(s, language):
    if not language:
        return s
    else:
        payload = {'q': s, 'target': language, 'key': API_KEY, 'format': 'html'}
        r = requests.post("https://translation.googleapis.com/language/translate/v2", params=payload)
        return html.unescape(json.loads(r.text)["data"]["translations"][0]["translatedText"])


def format_error(e):
    e = e.replace('<p>', '\n')
    e = e.replace('<br>', '\n')
    e = e.replace('</p>', '')
    e = e.replace('<pre> <code>', '>>>>>>>> CODE >>>>>>>> \n')
    e = e.replace('<pre><code>', '>>>>>>>> CODE >>>>>>>> \n')
    e = e.replace('</code> </pre>', '\n <<<<<<<< CODE <<<<<<<< \n')
    e = e.replace('</code></pre>', '\n <<<<<<<< CODE <<<<<<<< \n')
    e = e.replace('<code>', '**')
    e = e.replace('</code>', '**')
    e = e.replace('<li>', "\t-")
    e = e.replace('</li>', "")
   
    return e


def getStackOverflowAnswer(query):
    cse_url = "https://www.googleapis.com/customsearch/v1?cx=010246490594945788027:j77sj8npb9a&q=" + query + "&key=AIzaSyCX8ryZDLArnqXVE0kGnypl_luskiJa2zc"
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

    return (bodyHtml, link)

def insert_error(line, error, filename):
    f = open(filename, "r")
    contents = f.readlines()
    f.close()
    if line == len(contents):
        contents.append("\n")
        line+=1
    contents.insert(line, "\"\"\"\n" + error + "\n\"\"\"\n")

    f = open(filename, "w")
    contents = "".join(contents)
    f.write(contents)
    f.close()


def static_analysis(filename, language=None):
    payload = {'session_id': SESSION_ID}
    r = requests.delete(APP_ENDPOINT, params=payload)

    print(colored("Running static analysis...", 'blue'))
    p = os.popen('flake8 --ignore E ' + filename).read()
    if p == "":
        print(colored("No errors found.", 'green'))
    else:
        p = p.splitlines()
        line_numbers = []
        offset = 0
        for i, line in enumerate(p):
            line = line.split()
            error_file = line[0].split(':')
            error_line = int(error_file[1])
            error = ' '.join(line[2:])
            link = ''
            try:
                (sof, link) = getStackOverflowAnswer("python " + error)
                error = error  + "\nStackoverflow:\n" + sof
            except Exception:
                error = error
            error = error.replace("\n", "<br>")
            error = translate(error, language)
            error = format_error(error)
            line_numbers.append(str(error_line+offset))
            insert_error(error_line+offset, error, filename)
            payload = {'session_id': SESSION_ID, 'message': error, 'line_number': error_line+offset, 'file': filename, 'stack_url': link}
            r = requests.post(APP_ENDPOINT, params=payload)
            offset+=3+error.count('\n')
            
        print(colored("error lines: ", 'red') + ' '.join(line_numbers))



def run_program():
    try:
        exec(open("test1.py").read())
        print(colored('No errors detected', 'green'))
    except Exception:
        var = traceback.format_exc()
        print(colored("var: ", 'red') + var)


if __name__ == "__main__":
    print("Your ID is " + colored(SESSION_ID, "magenta"))
    filename = sys.argv[1]
    if len(sys.argv) > 2:
        language = lang_to_code(sys.argv[2])
        if language == "not found":
            print("Language not found")
        else:
            static_analysis(filename, language=language)
    else:
        static_analysis(filename)
