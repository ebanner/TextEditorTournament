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
        self.write_line("CONNECTION_ACCEPTED")
        super(ManagerConnection, self).run()
    
    def close(self):
        super(ManagerConnection, self).close()
        # remove from boss
        delattr(self.boss, 'manager')
