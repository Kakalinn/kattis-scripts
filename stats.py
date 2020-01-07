#!/usr/bin/env python3

import argparse
import configparser
import getpass
import os
import requests
import bs4
import urllib.parse
import sys
from datetime import *

sys.setrecursionlimit(10000)
# https://open.kattis.com/problems/mancala/statistics
def parse_row(sess, row):
    children = list(row.children)
    sid = children[0].text
    time = children[1].text
    problem = children[2].find('a').attrs['href'].split('/')[-1]
    status = children[3].text
    runtime = children[4].text
    lang = children[5].text

    if len(time) == 8:
        time = datetime.now().strftime('%Y-%m-%d ') + time
    time = datetime.strptime(time, '%Y-%m-%d %H:%M:%S')

    return (sid,time,problem,status,runtime,lang)

parser = argparse.ArgumentParser(description='Query Kattis submissions.')
parser.add_argument('-l', '--language', help="Lang.")
parser.add_argument('-e', '--list', help="List all langs.", action = 'store_true')
parser.add_argument('-p', '--prompt', help="Prompt for lang.", action = 'store_true')
parser.add_argument('problem', help="Problem.")
args = parser.parse_args()
problem = args.problem
submissions = []
submissions_lang = []
languages = []
padding = 2
lang = 'All languages'
if args.language:
    lang = args.language

sess = requests.Session()
res = sess.get('https://open.kattis.com/problems/%s/statistics/' % problem)
doc = bs4.BeautifulSoup(res.text, "html.parser")

for row in doc.select('.selectify-this'):
    languages = row.text.split('\n')[1:-1]

if args.list:
    print("Currently accepted languages are:")
    for i in range(1, len(languages)):
        print("  \"%s\"" % languages[i])
    sys.exit(0)

last = 0
for row in doc.select('.table tbody tr'):
    line = []
    children = list(row.children)
    if int(children[1].text) <= last:
        submissions.append(submissions_lang)
        submissions_lang = []
    last = int(children[1].text)
    if len(children) == 13:
        line.append(children[1].text)
        line.append(children[3].text)
        line.append(children[5].text)
        line.append(children[7].text)
        line.append(children[9].text)
    else:
        line.append(children[1].text)
        line.append(children[3].text)
        line.append(children[5].text)
        line.append('')
        line.append(children[7].text)
    submissions_lang.append(line)

if len(submissions_lang) != 0:
    submissions.append(submissions_lang)

if lang not in languages or args.prompt:
    if not args.prompt:
        print('There is no accepted submission in "%s"' % lang)
    print("Currently accepted languages are:")
    for i in range(1, len(languages)):
        print(i, end = '')
        if len(languages) > 9 and i < 10:
            print('.  ', end = '')
        else:
            print('. ', end = '')
        print('"%s"' % languages[i])
    print('Which one would you prefer ("0" for none)?')
    inp = input()
    if inp not in map(str, range(1, len(languages))):
        sys.exit(1)
    else:
        ind = int(inp)
        lang = languages[ind]
else:
    ind = languages.index(lang)

if ind != 0:
    for i in range(len(submissions[ind])):
        submissions[ind][i][3] = lang
cur_subs = submissions[ind]
heads = ['#', 'Name', 'Runtime', 'Language', 'Date']
maxes = []
for i in heads:
    maxes.append(len(i))

for i in range(len(cur_subs[0])):
    for j in range(len(cur_subs)):
        maxes[i] = max(maxes[i], len(cur_subs[j][i]))

for j in range(len(heads)):
    print(heads[j], end = '')
    for k in range(padding + maxes[j] - len(heads[j])):
        print(' ', end = '')
print()
for i in range(sum(maxes) + padding*len(heads)):
    print('-', end = '')
print()

for i in cur_subs:
    for j in range(len(i)):
        print(i[j], end = '')
        for k in range(padding + maxes[j] - len(i[j])):
            print(' ', end = '')
    print()
    
