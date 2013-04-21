import connection
import challenge
import time

NORMAL_MODE = 0
CHALLENGE_MODE = 1

class DisplayConnection(connection.Connection):
    """
    tbd
    
    """
    def __init__(self, socket, boss):
        """Keeps track of the socket and the file posing as the socket"""
        self.state = NORMAL_MODE
        super(DisplayConnection, self).__init__(socket, boss)

    def run(self):
        """ """
        self.write_line('CONNECTION_ACCEPTED')
        super(DisplayConnection, self).run()

    def send_participant_to_display(self, user, editor):
        self.write_line('ADD_PARTICIPANT')
        self.write_line(user)
        self.write_line(editor)

    def start_challenge(self):
        self.write_line('CHALLENGE_START')
        self.state = CHALLENGE_MODE

    def send_participant_forfeit_message(self, name):
        self.write_line('SET_PARTICIPANT_STATUS')
        self.write_line(name)
        self.write_line('STATUS_FORFEIT')

    def close(self):
        super(DisplayConnection, self).close()
        # remove from boss
        delattr(self.boss, 'display')
