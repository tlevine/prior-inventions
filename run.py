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
                'url': repository['url'].replace('https://api.github.com/repos/', 'https://github.com/'),
                'date': datetime.datetime.strptime(repository['pushed_at'], '%Y-%m-%dT%H:%M:%SZ') if repository['pushed_at'] else None,
                'description': description,
            }

        if repository['url'] == 'https://api.github.com/repos/tlevine/zoetrope' or 'link' not in r.headers:
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

EXHIBIT A: LIST OF PRIOR INVENTIONS AND ORIGINAL WORKS OF AUTHORSHIP EXCLUDED UNDER SECTION 4(a) CONFLICTING AGREEMENTS DISCLOSED UNDER SECTION 10(B)
===========================================================================================


The following is a list of (i) all inventions that belong solely to me or belong to me jointly with others, and
that relate in any way to any of the Company's actual or proposed businesses, products, services, or
research and development, and which are not assigned to the Company pursuant to this Agreement and (ii)
all agreements, if any, with a current or former client, employer, or any other person or entity, that may
restrict my ability to accept employment with the Company or my ability to recruit or engage customers or
service providers on behalf of the Company, or otherwise relate to or restrict my ability to perform my
duties for the Company or any obligation I may have to the Company:

'''

def footer():
    print '''
--------------------------------------------------------------------------

Except as indicated above on this exhibit, I have no inventions, improvements or original works to disclose
pursuant to Section 4(a) of this Agreement and no agreements to disclose pursuant to Section 10(b) of this
Agreement.

EMPLOYEE:
'''

def work(title, url, date, description):
    return '''
%(title)s
------------------------------------------------------------------------------------------------
**Title**: %(title)s

**Web address**: %(url)s

**Date**: %(date)s

**Abbreviated description**: %(description)s

''' % {'title':title,'url':url,'date':date.strftime('%B %Y') if date else 'Unknown',
    'description':description[:140] + '...' if len(description) > 0 else ''}

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
#       scraperwiki,
#       gitorious,
        manual,
        github_tlevine,
        github_csv,
        github_csvsoundsystem,
        github_appgen,
#       github_risley,
#       github_mapshit,
    ]:
        for _r in service():
            r = copy(_r)
            # print r['url']
            print work(r['title'].decode('utf-8'), r['url'].decode('utf-8'), r['date'], unidecode(r['description']))
    print '''
The following articles are included in the website www.thomaslevine.com
(https://github.com/tlevine/www.thomaslevine.com).

* About Thomas Levine
* Ampersands
* Attendees decide between statistics talks
* Arrays
* Bare domain redirect server
* BeagleBone Power Supply
* Tom Life Best Practices
* BetterCoach and the merits of the inferior schedule-finder
* Big Data Ergonomics
* Bits
* Bookmarks
* Inspiration for questions
* Burqua
* Scalable Big Data Cloud ROI Agile Fixie API with HTML9 Responsive Boilerstrap JS
* CentOS cluster slaves
* On balancing checkbooks
* Design for varied ability
* Christmas Gifts
* Citizen Science Resources
* Couch-style data versioning in sqlite
* Covariance drawings
* Curriculum vitae
* Data business models
* Meeting nice people at DataKind events
* Another definition of "big data"
* The mindset of data science
* A new email address
* Local ScraperWiki Library
* DumpTruck Version 0.0.3
* Earmuffs
* Emergency Exit Only
* English and American
* Everyday Living for Girls
* Do all "analysts" use Excel?
* Foo
* Films I like
* Five stages of PhD
* FMS Symphony
* gastronomify
* Gullible
* Words that are hard to spell
* Hacks Hackers Buenos Aires Media Party
* Higher-power distance measures
* Hip 'Data' Terms
* The Hovering Cycle
* htmltable2matrix
* imapfilter
* My personal computer infrastructure
* Jaywalking
* Nude Jello Wrestling
* Where do people position computer keyboards?
* Klout jump on May 25
* Materials for leaning Angular
* Learn Computers Through ______
* Arrays
* On listening
* My appointment and termination at my high school newspaper
* Measuring Skin Temperature
* Prevalence of Middle Names
* Microfinance Data Scraping
* Moments of a function
* Effect of the number pad on mousing location
* Movies I like
* News Hack Day SF
* Addiction Recovery Meetings
* New York Pizza
* Open by default
* Open data licensing
* Open data possibilities
* OpenPrism
* The Orpheus Myth
* How I parse PDF files
* pbdq
* How principle component analysis works
* Industrial Remote-Controlled Peanut Butterers Parts & Supplies and Bagels Company
* Pirate Trends
* Preserving whitespace in haml
* Random Person of the Week
* R graphics tricks that you probably shouldn't use
* Real World Algorithms
* Reciprocity
* The Ridership Rachenitsa
* Unsanitary conditions in dormitory bathrooms
* R spells for data wizards
* cRowdsouRcing
* Capital projects
* Assessed property values
* Where does the "market value" on your tax bill come from?
* Scarsdale High School bus schedule weirdness
* Scarsdale Village tax rates and inflation
* Changes in appropriations to Scarsdale Village funds
* Scarsdale data journalism
* scp wrapper
* Handling exceptions in scrapers
* Installing Selenium
* Multisensory data experiences
* setxkbmap aliases
* Shakespeare on the internet
* Tests for your shell
* Soap-dispenser placement
* Open Calendars
* What's in a count?
* What file formats are on the data portals?
* Progeny of Ten Socrata Datasets
* How to use Socrata's site metrics API
* Analyze all the datasets
* Who uses Socrata's analysis tools?
* Statistics through doodles
* The Street Sign Protocol
* What's in a table?
* Teaching Data Science
* Tea Party
* Searching lots of inconveniently formatted files at once
* Terminal history
* Things to think about when you're building products on open data
* Things to read
* tmux aliases
* treasury.io
* Why does turning into a zombie seem unpleasant?
* Twinkle
* Twitter Scraper Library
* Why don't people use this reading room?
* URL Encoding and Decoding
* Utlity of Cobalt
* My visit to Socrata, and data analysis about data analysis
* Things I want
* What I think people who want to learn programming
* World -> Data -> World
* Datestamped archives of a webpage
    '''

if __name__ == '__main__':
    main()
