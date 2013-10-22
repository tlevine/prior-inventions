#!/usr/bin/env python
"List Tom's prior inventions and original works of authorship."
import json, base64, datetime
from lxml.html import fromstring
from helpers import get
import chomsky as c
from unidecode import unidecode
from copy import copy
import requests
import os

GITHUB_QUERYSTRING = 'access_token=' + os.environ['GITHUB_TOKEN'] if 'GITHUB_TOKEN' in os.environ else ''
TODAY = datetime.date.today()

def scraperwiki_date(relative_date):
    'Convert ScraperWiki relative times to absolute times.'
    if relative_date == 'Created 1 year ago.':
        years = 1
        months = 0

    elif relative_date == 'Created 2 years ago.':
        years = 2
        months = 0

    elif 'week' in relative_date:
        matcher = c.Literal('Created ') + c.Chars('0123456789') + c.Any(c.Literal(' months, '), c.Literal(' month, ')) + c.Chars('0123456789') + c.Literal(' weeks ago.')
        years = 0
        months = int(matcher(relative_date)[1])

    else:
        matcher = c.Literal('Created 1 year, ') + c.Chars('0123456789') + c.Any(c.Literal(' month ago.'), c.Literal(' months ago.'))
        years = 1
        months = int(matcher(relative_date)[1])

    return TODAY + datetime.timedelta(years, months)

def scraperwiki():
    for i in range(1,14 + 1):
        raw = get('https://classic.scraperwiki.com/profiles/tlevine/?page=%d' % i).read()
        html1 = fromstring(raw)
        for repository in html1.xpath('//li[@class="code_object_line"]'):
            a = repository.xpath('descendant::h3/a[position()=2]')[0]
            title = a.xpath('text()')[0]
            url = 'https://classic.scraperwiki.com' + a.xpath('@href')[0]
            relative_date = html1.xpath('descendant::p[@class="context"][position()=2]/text()')[0].strip()
            date = scraperwiki_date(relative_date)
            if url == 'https://classic.scraperwiki.com/scrapers/tahrirsupplies_map/':
                continue
            # print url
            html2 = fromstring(get(url).read())
            description = html2.get_element_by_id('divAboutScraper').text_content()
            yield {
                'title': title,
                'url': url,
                'date': date,
                'description': description,
            }

def gitorious():
    project = fromstring(get('https://gitorious.org/tlevine.xml').read().encode('utf-8'))
    for repository in project.xpath('//repository[owner[text()="tlevine"]]'):
        title = repository.xpath('name/text()')[0]
        repository2 = fromstring(get('https://gitorious.org/tlevine/%s.xml' % title).read().encode('utf-8'))
        d = repository2.xpath('last-pushed-at/text()')
        yield {
            'title': title,
            'url': 'https' + repository.xpath('clone_url/text()')[0][3:-4],
            'date': None if d == [] else datetime.datetime.strptime(d[0], '%Y-%m-%dT%H:%M:%SZ'),
            'description': '\n'.join(repository2.xpath('description/text()')),
        }

def github(username):
    'Get my GitHub repositories.'
    url = "https://api.github.com/users/%s/repos" % username
    while True:
        r = requests.get(url + '?' + GITHUB_QUERYSTRING)
        for repository in json.loads(r.text):
            d = json.load(get(repository['url'] + '/readme?' + GITHUB_QUERYSTRING))
            if d.get('message') == 'Not Found':
                description = ''
            else:
                description = base64.decodestring(d.get('content', ''))

            yield {
                'title': repository['name'],
                'url': repository['url'],
                'date': datetime.datetime.strptime(repository['pushed_at'], '%Y-%m-%dT%H:%M:%SZ') if repository['pushed_at'] else None,
                'description': description,
            }

        if repository['url'] == 'https://api.github.com/repos/tlevine/zoetrope':
            break

        url = r.headers['link'].split(';')[0][1:-1]

github_tlevine = lambda: github('tlevine')
github_csv = lambda: github('csv')
github_csvsoundsystem = lambda: github('csvsoundsystem')
github_appgen = lambda: github('appgen')
github_risley = lambda: github('risley')
github_mapshit = lambda: github('mapshit')

def header():
    return '''
EXHIBIT A: LIST OF PRIOR INVENTIONS AND ORIGINAL WORKS OF AUTHORSHIP EXCLUDED UNDER SECTION 4(a)
================================================================================================
'''

def work(title, url, date, description):
    return '''
%(title)s
------------------------------------------------------------------------------------------------
**Title**: %(title)s

**Web address**: %(url)s

**Date**: %(date)s

**Description**: %(description)s













''' % {'title':title,'url':url,'date':date.strftime('%B %Y') if date else 'Unknown','description':description}

def manual():
      yield {
          'title': 'Simple Webcam',
          'url': 'https://chrome.google.com/webstore/detail/simple-webcam/cejgmnpegppdhkmmgmdobfelcdgfhkmo?hl=en',
          'date': datetime.date(2012, 10, 15),
          'description': "Simple Webcam is a webcam app for Chrome that just works. Open the app, click one button, then save your picture. That's it.",
      }

def main():
    print header()
    for service in [
        scraperwiki,
        gitorious,
        manual,
        github_tlevine,
        github_csv,
        github_csvsoundsystem,
        github_appgen,
        github_risley,
        github_mapshit,
    ]:
        for _r in service():
            r = copy(_r)
            # print r['url']
            print work(r['title'].decode('utf-8'), r['url'].decode('utf-8'), r['date'], unidecode(r['description']))

if __name__ == '__main__':
    main()
