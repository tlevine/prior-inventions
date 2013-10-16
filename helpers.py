#!/usr/bin/env python
'From hardhat https://github.com/scraperwiki/hardhat/blob/master/hardhat/hardhat.py'

import os
import re

import urllib
from urlparse import urljoin

def get(url, cachedir = '.'):
    'Download a web file, or load the version from disk.'
    tmp1 = re.sub(r'^https?://', '', url)
    tmp2 = [cachedir] + filter(None, tmp1.split('/'))
    local_file = os.path.join(*tmp2)
    local_dir = os.path.join(*tmp2[:-1])
    del(tmp1)
    del(tmp2)

    # mkdir -p
    if not os.path.exists(local_dir):
        os.makedirs(local_dir)

    # Download
    if not os.path.exists(local_file):
       urllib.urlretrieve(url, filename = local_file)

    return open(local_file)
