#!/usr/bin/python3

import sys
import time
import threading
import atexit

connected = False


def on_exit():
      """Just change terminal colors back to normal."""
      print("\033[0m", end = "")
      

class Receiver(threading.Thread):
      """
      Receiver just reads data and prints it to the screen (so it doesn't block
      the user)
      """
      def __init__(self, client):
            threading.Thread.__init__(self)
            self.client = client;
      
      def run(self):
            global connected
            while True:
                  try:
                        message = read_data(self.client)
                        print("\r\033[93mClient: " + message.decode('utf-8') + "\033[94m")
                  except Exception:
                        print("\033[0mClient Disconnected. Type anything to quit.")
                        connected = False
                        break

def read_line(sock_stream):
      """Returns a line read from the submission server socket."""
      line = sock_stream.readline().strip()
      print('READ: {}'.format(line))
      return line


if __name__ == '__main__':
      # register exit action (function)
      atexit.register(on_exit)
      
      time.sleep(5)
      print("Just so you know, this code doesn't actually do anything.")
