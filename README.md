Text Editor Tournament
=======================

Client-server system connecting together multiple tournament participants, a
manager (administrator), and a web-based display frontend system through a
central server.

The server handles distributing challenges submitted by the manager and
submissions of answers by the participants. The server and client programs are
written in Python 3. The web-based frontend displays information about the
tournament in real-time using the HTML5 canvas and WebSockets.

Overview
========

The course of events that transpire in a typical tournament are as follows:

1) Start Submission server
2) Start Display server
3) Start Display web client
4) Start Manager
5) Have clients connect
6) Load up a challenge
7) Start the challenge
8) Repeat steps 6 through 8

Start Submission Server
=======================

The most important piece of running a tournament is to start the central server
that all clients must register with in order to talk to each other. The
submission server is the effective brain of this competition software that
allows every client registers with (e.g. the manager, participants, display).

Start the submission server by opening a terminal, traversing into `server`, and
issuing the following command:

    $ python3 submission_server.py

The Submission server will be running on port 6900.

Start Display Server
====================

Next up is hooking up the web front end to the submission server so we can view
the results in real time. The first step in this process is to start the Display
server that will relay challenge statistics from the Submission server to the
Display web client.

To start the Display server, open a terminal, traverse into `display`, and issue
the following command:

    $ python3 ws.py

This Display server listens on port 9999 and assumes the Submission server is
running on port 6900.

Start Display web client
========================

The Display server needs a client to relay the tournament statistics it
recieves from the Submission server. Create such a client by opening
`index.html` with your favorite web browser (e.g. Firefox, Chrome, etc.)

Note: the Display client assumes the Display server is running on the same
machine. In order to run the Display server on another machine, change the
**SERVER_ADDR** line in `main.js` to the IP address of the machine the Display
server is running on.

Start Submission server
=======================

Open a termial and traverse into `server/`. Issue the following command:

    $ python3 submission_server.py

The submission server by default runs on port 6900. This port can be changed at
the command line. For instance, to run the submission server on port 3017, issue
the following command instead:

    $ python3 submission_server.py 3017

Keep in mind that the Display server expects the Submission server to be running
on port 6900, so you would need to change where the Display server expects the
Submission server to be running (this feature is not yet supported).

Start Manager
=============

Open a terminal, traverse into `manager`, and issue the following command:

    $ python3 manager.py

The manager is the interface by which challenges are loaded and initiated. Once
the manager has been accepted by the submission server, the following commands
are recognized:

* <load | send | submit> <challenge_id> <challenge_name>
    * Alert the boss the new challenge is now <challenge_name> with a challenge
      name of <challenge_id>. Note: <challenge_name> must be a challenge in the
      same directory as manager.py.
* <init>
    * Send out the challenge to all registered participants. Note: there must
      already be a challenge that was loaded with the above command.
* <ls>
    * List all challenges in the current directory.
* <exit | quit>
    * Exit the manager.

Have clients connect
====================

For every participant, have them supply them with `participant.py` and have them
issue the following if the Submission server is on the same machine that they
are on:

    $ python3 participant.py [submission_server_ip]

where **submission_server_id** is the IP address of the machine that the
Submission server is running on.

The participants are then prompted to enter their name and editor they are
using. They must then wait for the manager to Load up a Challenge.

Load up a Challenge
===================

Issue the <load | send | submit> command from the manager's prompt with a legal
challenge.

Start the challenge
===================

The manager can then issue the **init** command and every participant will be
sent the challenge description and will be prompted to accept it. Once all
participants have responded, the manager can then start the challenge or cancel
it. If the manager starts the challenge then the challenge will continue until
every participant has either successfully completed it or forfeited.
