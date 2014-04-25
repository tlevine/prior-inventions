#!/usr/bin/env python3
import sys
import itertools
import json

import requests

def page(page_number:int):
    response = requests.get('https://api.github.com/users/tlevine/repos', params = {'page': page_number})
    return json.loads(response.text)

def pages():
    for page_number in itertools.count(1):
        yield page(page_number)

def repositories():
    for the_page in itertools.takewhile(lambda r: r != [], pages()):
        yield from the_page

def main():
    for repository in repositories():
        sys.stdout.write(repository['html_url'] + '\n')

if __name__ == '__main__':
    main()
