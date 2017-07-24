#coding=UTF-8
import socket
import json
import hashlib
import time

sk = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

def getAccount():
    username = ''
    while (not username.isalnum()) or (not username):
        print('<<< Username(alpha and digit only, not null): '),
        username = raw_input()
    password = ''
    while (not password.isalnum()) or (not password):
        print('<<< Password(like above): '),
        password = raw_input()
    return (username, password)

def sha256(s):
    return hashlib.sha256(s).hexdigest()

def getTime():
    return time.asctime(time.localtime(time.time()))

print(">>> Welcome to Chat.")
print(">>> Connecting to server...")
sk.connect(('127.0.0.1', 31415))
print(">>> Successfully connect to server.")
print(">>> Welcome message recieved:")
data = sk.recv(1024)
print(data)

print(">>> Register a new account? (y/n) [default: n] "),
inp = raw_input()
# register
if inp == 'y':
    # get account data
    un, pw = getAccount()
    # generate data
    data = { }
    data['type'] = 'reg'
    data['username'] = un
    data['password'] = sha256(pw)
    ds = json.dumps(data)
    # send, respond
    sk.send(ds)
    rs = sk.recv(1024)
    resp = json.loads(rs)
    print(resp['data'])

# login
print('\n\n>>> Login: Please enter your info.')
key = ''
username = ''
while True:
    un, pw = getAccount()
    data = { }
    data['type'] = 'login'
    data['username'] = un
    data['password'] = sha256(pw)
    ds = json.dumps(data)
    # send, respond
    sk.send(ds)
    rs = sk.recv(1024)
    resp = json.loads(rs)
    if (resp['success'] == 1):
        key = resp['key']
        username = un
        break
    else:
        print('>>> Auth failed: %s' % resp['data'])
        continue

# chat
print('\n\n\n>>> User %s login successfully.' % username)
while True:
    print('>>> Menu: (a) Send a message | (b) Read all messages | (c) Logout && Exit')
    print('>>> Choose an option (default: a) '),
    inp = raw_input()
    # read messages
    if inp == 'b':
        print('>>> Loading messages...')
        data = { }
        data['type'] = 'get'
        data['username'] = username
        data['key'] = key
        sk.send(json.dumps(data))
        resp = json.loads(sk.recv(1024))
        if resp['success'] == 0:
            print('>>> Load failed: %s' % resp['data'])
            continue
        else:
            print('>>> Message List:\n\n')
            for x in resp['data']:
                print x['user'], x['time']
                print x['text']
                print "\n"
            continue
        continue
    # exit
    if inp == 'c':
        print('>>> Goodbye!')
        break
    # send message
    print('>>> Enter your message: '),
    txt = raw_input()
    data = { }
    data['type'] = 'send'
    data['username'] = username
    data['key'] = key
    data['time'] = getTime()
    data['text'] = txt
    sk.send(json.dumps(data))
    resp = json.loads(sk.recv(1024))
    if resp['success'] == 1:
        print('>>> Success.')
    else:
        print('>>> Failure: %s' % resp['data'])
    continue

# stop connection
sk.send(json.dumps({'type': 'exit'}))
sk.close()
