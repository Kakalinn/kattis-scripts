#!/usr/bin/env python3

# Dependencies:
#   python3
#   the request package for python 3
#   bs4 (Beautiful soup 4)
#
# Examples:
#   ./query.py
#       - Shows a list of your last few submissions.
#   ./query.py -c 10
#       - Shows a list of your 10 latest submissions.
#   ./query.py -c 5 --problems 3sideddice hello carrots digbuild
#       - Shows you your five latest submission to 3sideddice, hello,
#         carrots, digbuild (so in total, up to 20 submissions).
#   ./query.py -c 10 -f
#       - Shows a color-coded list of your 10 latest submissions.
#   ./query.py -c 10 -f -p
#       - Shows a color-coded list of your 10 latest submissions, but
#         instead of looking for a .kattisrc file it prompts you for
#         a username and password.


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

def ncmp(a, b, n):
    # for scored problems to register as accepted
    i = 0
    while n > 0:
        if len(a) - i == 0 or len(b) - i == 0 or a[i] != b[i]:
            return False
        i += 1
        n -= 1
    return True

def prompt_login():
    print('Username: ', end = '')
    username = input()
    password = getpass.getpass()
    return {'user': username, 'password': password, 'script': 'true'}

no_submissions = 7
parser = argparse.ArgumentParser(description='Query Kattis submissions.')
parser.add_argument('-f', '--format', help="Formats the output depending on ech submissions status.", action = 'store_true')
parser.add_argument('-c', '--count', help="The number of submissions to query. Default is %d. Use -1 for unlimited submissions." % no_submissions)
parser.add_argument('-p', '--prompt', help="Force a password prompt, skipping .kattisrc, for login.", action = 'store_true')
parser.add_argument('-s', '--sieve', help="Output only submission to the problems with the given problem IDs.", nargs = '+')
parser.add_argument('--problems', help="Print COUNT submissions for the given problems, in the order given.", nargs = '+')
parser.add_argument('--minimal', help="Print only the status of the submissions.", action = 'store_true')
args = parser.parse_args()
if args.format:
    format_bold = '\033[1m'
    format_green = '\033[92m'
    format_yellow = '\033[93m'
    format_red = '\033[91m'
    format_end = '\033[0m'
else:
    format_bold = ''
    format_green = ''
    format_yellow = ''
    format_red = ''
    format_end = ''

sieve = None
problems = args.problems
if args.sieve:
    sieve = set(args.sieve)

recent_submissions = []
pcnt = []
max_sid_length = 0
max_problemname_length = 0
max_status_length = 0
max_lang_length = 0
if args.count:
    no_submissions = int(args.count)
sess = requests.Session()

if args.prompt:
    login_data = prompt_login()
else:
    cfg = configparser.ConfigParser()
    if os.path.exists('/etc/kattis/submit/kattisrc'):
        cfg.read('/etc/kattis/submit/kattisrc')

    if not cfg.read([os.path.join(os.getenv('HOME'), '.kattisrc'), os.path.join(os.path.dirname(sys.argv[0]), '.kattisrc')]):
        print("No .kattisrc found in default locations (home and current directory). Falling back on login promtp.")
        login_data = prompt_login()
    else:
        username = cfg.get('user', 'username')
        password = token = None
        try:
            password = cfg.get('user', 'password')
        except configparser.NoOptionError:
            pass
        try:
            token = cfg.get('user', 'token')
        except configparser.NoOptionError:
            pass
        if password is None and token is None:
            print("Neither password or token found in .kattisrc. It may be corrupt. Falling back on login promtp.")
            login_data = prompt_login()
        else:
            login_data = {'user': username, 'script': 'true'}
            if password:
                login_data['password'] = password
            if token:
                login_data['token'] = token

login_req = sess.post('https://open.kattis.com/login/email', data=login_data)
login_html = bs4.BeautifulSoup(login_req.text, "html.parser")

if login_req.status_code != 200:
    print('Login failed.')
    if login_req.status_code == 403:
        print('Incorrect username or password/token (403)')
    elif login_req.status_code == 404:
        print('Incorrect login URL (404)')
    else:
        print('Status code:', login_reply.status_code)
    sys.exit(1)

if args.problems is not None:
    #https://open.kattis.com/users/kakali/submissions/sumsets
    for problem in problems:
        cnt = 0
        page = 0
        tmpns = no_submissions
        while tmpns != 0:
            res = sess.get('https://open.kattis.com/users/%s/submissions/%s?page=%d' % (login_data['user'],problem,page))
            doc = bs4.BeautifulSoup(res.text, "html.parser")
            found = False
            for row in doc.select('.table-submissions tbody tr'):
                found = True
                children = list(row.children)
                if len(children) <= 3:
                    continue

                recent_submissions.append(parse_row(sess, row))
                cnt += 1
                max_sid_length = max(max_sid_length, len(recent_submissions[-1][0]))
                max_problemname_length = max(max_problemname_length, len(recent_submissions[-1][2]))
                max_status_length = max(max_status_length, len(recent_submissions[-1][3]))
                max_lang_length = max(max_lang_length, len(recent_submissions[-1][4]))
                tmpns -= 1
                if tmpns == 0:
                    break

            if not found:
                break
            page += 1
        pcnt.append(cnt)
else:
    page = 0
    while no_submissions != 0:
        res = sess.get('https://open.kattis.com/users/%s?page=%d' % (login_data['user'],page))
        doc = bs4.BeautifulSoup(res.text, "html.parser")
        found = False
        for row in doc.select('.table-submissions tbody tr'):
            found = True
            children = list(row.children)
            if len(children) <= 3:
                continue

            recent_submissions.append(parse_row(sess, row))
            max_sid_length = max(max_sid_length, len(recent_submissions[-1][0]))
            max_problemname_length = max(max_problemname_length, len(recent_submissions[-1][2]))
            max_status_length = max(max_status_length, len(recent_submissions[-1][3]))
            max_lang_length = max(max_lang_length, len(recent_submissions[-1][4]))
            no_submissions -= 1
            if no_submissions == 0:
                break

        if not found:
            break
        page += 1
    if no_submissions > 0:
        print("Warning: Number of requested submissions is larger than total submissions of account.")

for e in recent_submissions:
    if args.minimal:
        print(e[3])
    else:
        if sieve is None or e[2] in sieve:
            if ncmp(e[3], 'Accepted', 8):
                print(format_bold, end = '')
            print(e[0], end = '')
            for i in range(4 + max_sid_length - len(e[0])):
                print(' ', end = '')
            print(e[1], e[2], end = '')
            for i in range(4 + max_problemname_length - len(e[2])):
                print(' ', end = '')
            if ncmp(e[3], 'Accepted', 8):
                print(format_green, end = '')
            elif ncmp(e[3], 'New', 3) or ncmp(e[3], 'Running', 7) or ncmp(e[3], 'Judge', 5):
                print(format_yellow, end = '')
            else:
                print(format_red, end = '')
                
            print(e[3], end = format_end)
            for i in range(4 + max_status_length - len(e[3])):
                print(' ', end = '')
            print(e[4], end = '')
            for i in range(4 + max_lang_length - len(e[4])):
                print(' ', end = '')
            print(e[5], end = '')
            if ncmp(e[3], 'Accepted', 8):
                print (format_end)
            else:
                print()

if args.problems is not None:
    print("Number of submission per problem")
    for i in range(len(pcnt)):
        print(problems[i], "-", pcnt[i])
