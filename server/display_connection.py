import connection
import challenge
import time

class DisplayConnection(connection.Connection):
    """
    tbd
    
    """
    def __init__(self, socket, boss):
        """Keeps track of the socket and the file posing as the socket"""
        super(DisplayConnection, self).__init__(socket, boss)

    def run(self):
        """ """
        self.write_line("CONNECTION_ACCEPTED")
        super(DisplayConnection, self).run()
    
    def close(self):
        super(DisplayConnection, self).close()
        # remove from boss
        delattr(self.boss, 'display')
