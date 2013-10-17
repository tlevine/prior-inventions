#!/bin/sh
set -e

echo 'The following articles are included in this website.'
echo
grep ^title: ~/Documents/www.thomaslevine.com/content/\!/*/index.md|cut -d: -f3|sed s/^/*/
