#!/usr/bin/env python3
import sys
import itertools
import json

import lxml.html
from picklecache import get

def github():
    def pages():
        for page_number in itertools.count(1):
            response = get('https://api.github.com/users/tlevine/repos', params = {'page': page_number})
            for repository in json.loads(response.text):
                yield repository['html_url']

    for the_page in itertools.takewhile(lambda r: r != [], pages()):
        yield from the_page

def thomaslevine():
    response = get('http://thomaslevine.com/!/')
    html = lxml.html.fromstring(response.text)
    return map(str, html.xpath('//a'))

def main():
    for link in itertools.chain(thomaslevine(), github()):
        sys.stdout.write('%s\n' % link)

if __name__ == '__main__':
    main()
