#this is the client from which users will submit their text files

from ftplib import FTP_TLS
ftps = FTP_TLS()
ftps.connect('localhost', 2100)
ftps.login('user', '12345')     # login
ftps.prot_p()                   # switch to secure data connection
ftps.retrlines('LIST')          # list directory content securely
