#this is the client from which users will submit their text files

import sys
from ftplib import FTP

ftp = FTP()
ftp.connect('localhost', 2100)
ftp.login('user', '12345')     # login
#ftp.retrlines('LIST')          # list directory contents
ftp.storlines("STOR " + str(sys.argv[1]), open(str(sys.argv[1])))
