#!/bin/sh

if which python2 > /dev/null; then
	p=python2
else
	p=python
fi
$p run.py > inventions.md
