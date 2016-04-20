#!/bin/bash

ru=locale/ru/LC_MESSAGES
en=locale/en/LC_MESSAGES

rm -f $ru/messages.mo
rm -f $en/messages.mo

msgfmt -o $ru/messages.mo $ru/messages.po
msgfmt -o $en/messages.mo $en/messages.po

