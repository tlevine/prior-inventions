#!/usr/bin/env python3
import re
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

def scraperwiki():
    for page_number in itertools.count(1):
        url = 'https://classic.scraperwiki.com/profiles/tlevine/?page=%d' % page_number
        response = get(url)
        html = lxml.html.fromstring(response.text)
        html.make_links_absolute(url)
        for href in html.xpath('//li[@class="code_object_line"]/descendant::h3/a[position()=2]/@href'):
            yield re.sub(r'index.html$', '', str(href))

def main():
    for link in itertools.chain(scraperwiki(), thomaslevine(), github()):
        sys.stdout.write('%s\n' % link)

if __name__ == '__main__':
    main()
