import connection
import challenge
import time
import operator

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

    def send_forfeit_message(self, name):
        self.write_line('SET_PARTICIPANT_STATUS')
        self.write_line(name)
        self.write_line('STATUS_FORFEIT')

    def send_incorrect_submission_message(self, name):
        self.write_line('INCORRECT_SUBMISSION')
        self.write_line(name)

    def send_finished_message(self, name):
        self.write_line('SET_PARTICIPANT_STATUS')
        self.write_line(name)
        self.write_line('STATUS_FINISHED')

    def close(self):
        super(DisplayConnection, self).close()
        # remove from boss
        delattr(self.boss, 'display')

    def send_challenge_finished(self, participants):
        self.write_line('CHALLENGE_FINISH')

        # Get a dictionary of each editor to a list of times for that editor
        editor_times = {}
        for participant in participants:
            if participant.forfeited or not participant.challenge_accepted:
                # Don't send over information about a participant if that
                # participant forfeited.
                continue
            elif participant.editor not in editor_times:
                editor_times[participant.editor] = [int(participant.time * 1000)]
            else:
                editor_times[participant.editor].append(
                        int(participant.time * 1000))

        print('Editor times: {}'.format(editor_times))
        # Compute the minimum time for every editor
        minimum_times = [ 
                (editor, min(times)) for editor, times in editor_times.items() ]
        # Sort the editors in ascending time
        minimum_times.sort(key=operator.itemgetter(1))
        print('Minimum times sorted: {}'.format(minimum_times))

        # Send over each of the minimum editor times in order
        for editor, minimum_time in minimum_times:
            self.write_line(editor)
            self.write_line(str(minimum_time))
        self.write_line('MINIMUM_EDITOR_TIMES_STATISTIC_END')

        # Send completion time for every participant in order of best time first
        parts = [ (p.user, p.editor, int(p.time * 1000)) for p in participants
                if not p.forfeited and p.challenge_accepted ]
        parts.sort(key=operator.itemgetter(2))
        for part in parts:
            self.write_line(part[0])
            self.write_line(part[1])
            self.write_line(str(part[2]))
        self.write_line('INDIVIDUAL_PARTICIPANT_STATISTICS_END')

        # Send the average time for all the participants as a whole
        times = [ participant.time for participant in participants if not
                participant.forfeited and participant.challenge_accepted ]
        if times:
            # At least one participant finished
            self.write_line(str(int(sum(times)/len(times) * 1000)))
        else:
            # No one actually finished without forfeiting
            self.write_line('-1')
