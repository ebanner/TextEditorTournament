# manager.py
import connection

class ManagerConnection(connection.Connection):
    """
    tbd
    
    """
    def check_message(self, message):
        """ """
        print(message)
        super(ManagerConnection, self).check_message(message)
        
    def run(self):
        """ """
        super(ManagerConnection, self).run()
