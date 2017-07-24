#coding=UTF-8
import socket
import threading
import time
import json
import hashlib
import random

userinfo = {}
userkey = {}
messages = []
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

def sha256(s):
    return hashlib.sha256(s).hexdigest()

def checkName(name):
    for x in userinfo.keys():
        if x == name:
            return False
    return True

def tcplink(sock, addr):
    print('Accept new connection from %s:%s' % addr)
    sock.send('Welcome here.\nServer version: 0.0.1')
    while True:
        rs = sock.recv(1024)
        time.sleep(1)
        if (not rs):
            continue
        resp = json.loads(rs)
        print resp
        if resp['type'] == 'exit':
            # close connection
            print('Exit message recieved.')
            break
        if resp['type'] == 'reg':
            # register request
            data = { }
            if not checkName(resp['username']):
                data['data'] = 'Fail: Username has been used.'
                ds = String(json.dumps(data))
                sock.send(ds)
                continue
            userinfo[resp['username']] = resp['password']
            data['data'] = 'Success.'
            ds = json.dumps(data)
            sock.send(ds)
            print userinfo
            continue
        if resp['type'] == 'login':
            # login request
            data = { }
            if checkName(resp['username']):
                # username not exist
                data['success'] = 0
                data['data'] = 'Username not exist.'
                sock.send(json.dumps(data))
                continue
            if userinfo[resp['username']] == resp['password']:
                # pass
                key = sha256(str(random.randint(1, 100000)))
                userkey[resp['username']] = key
                data['key'] = key
                data['success'] = 1
                sock.send(json.dumps(data))
                continue
            else:
                # wrong password
                data['success'] = 0
                data['data'] = 'Wrong password.'
                sock.send(json.dumps(data))
                continue
        if resp['type'] == 'send':
            # send request
            data = { }
            if checkName(resp['username']):
                # username not exist
                data['success'] = 0
                data['data'] = 'Username not exist.'
                sock.send(json.dumps(data))
                continue
            if userkey[resp['username']] != resp['key']:
                # wrong password
                data['success'] = 0
                data['data'] = 'Wrong password.'
                sock.send(json.dumps(data))
                continue
            else:
                # pass
                item = {}
                item['user'] = resp['username']
                item['time'] = resp['time']
                item['text'] = resp['text']
                messages.append(item)
                data['success'] = 1
                sock.send(json.dumps(data))
                continue
        if resp['type'] == 'get':
            data = { }
            if checkName(resp['username']):
                # username not exist
                data['success'] = 0
                data['data'] = 'Username not exist.'
                sock.send(json.dumps(data))
                continue
            if userkey[resp['username']] != resp['key']:
                # wrong password
                data['success'] = 0
                data['data'] = 'Wrong password.'
                sock.send(json.dumps(data))
                continue
            else:
                # pass
                data['success'] = 1
                data['data'] = messages
                sock.send(json.dumps(data))
                continue
    sock.close()
    print('Close connection from %s:%s' % addr)

s.bind(('127.0.0.1', 31415))
s.listen(5)
print('Server start successfully, listenning...')
while True:
    sock, addr = s.accept()
    t = threading.Thread(target=tcplink, args=(sock, addr))
    t.start()
s.close()
