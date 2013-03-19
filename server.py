#server from which we will receive the text file submissions (for judging/grading)

from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import FTPHandler
from pyftpdlib.servers import FTPServer

authorizer = DummyAuthorizer()
authorizer.add_user("user", "12345", "/home/student/willigcl193/Desktop", perm="elradfmw")
#authorizer.add_anonymous("/home/nobody")

handler = FTPHandler
handler.authorizer = authorizer

server = FTPServer(("127.0.0.1", 2100), handler)
server.serve_forever()
