#!/usr/bin/env python3
import sys
import itertools
import json

import lxml.html
from picklecache import get

def github():
    def pages():
        for page_number in itertools.count(1):
            response = get('https://api.github.com/users/tlevine/repos?page=%d' % page_number)
            for repository in json.loads(response.text):
                yield repository['html_url']

    for link in itertools.takewhile(lambda r: r != [], pages()):
        yield link

def thomaslevine():
    url = 'http://thomaslevine.com/!/'
    response = get(url)
    html = lxml.html.fromstring(response.text)
    html.make_links_absolute(url)
    return (str(link) for link in html.xpath('//a/@href') if link.startswith(url))

def main():
    for link in itertools.chain(thomaslevine(), github()):
        sys.stdout.write('%s\n' % link)

if __name__ == '__main__':
    main()
