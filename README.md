Text Editor Tournament
=======================

Client-server system connecting together multiple tournament participants, a
Manager (administrator), and a web-based display frontend system through a
central server.

The server handles distributing challenges submitted by the Manager and
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

The most important piece of running a tournament is the Submission server.
Clients of every type (e.g. Manager, participants, display) must register with
the Submission server. Simply put, it is the brain of the tournament.

Start the submission server by opening a terminal, traversing into `server/`, and
issuing the following command:

    $ python3 submission_server.py

The Submission server will be running on port 6900.

Start Display Server
====================

Next up is hooking up the web front end to the Submission server so we can view
results in real time. The first step in this process is to start the Display
server. The Display server relays challenge statistics from the Submission
server to the Display web client.

To start the Display server, open a terminal, traverse into `display/`, and issue
the following command:

    $ python3 ws.py

This Display server listens on port 9999 and assumes the Submission server is
running on port 6900.

Start Display web client
========================

The Display server needs a client to relay the tournament statistics it
recieves from the Submission server. Create such a client by opening
`index.html` in `display` with your favorite web browser (e.g. Firefox, Chrome,
etc.)

**Note:** the Display client assumes the Display server is running on the same
machine. In order to run the Display server on another machine, change the
**SERVER_ADDR** value line in `main.js` to the IP address of the machine the
Display server is running on.

Start Submission server
=======================

Open a termial and traverse into `server/` and issue the following command:

    $ python3 submission_server.py

The submission server by default runs on port 6900. This port can be changed at
at invocation. For instance, to run the submission server on port 3017, issue
the following command instead:

    $ python3 submission_server.py 3017

Keep in mind that the Display server expects the Submission server to be running
on port 6900, so you would need to change where the Display server expects the
Submission server to be running (this feature is not yet supported).

Start Manager
=============

Open a terminal, traverse into `Manager/`, and issue the following command:

    $ python3 Manager.py

The Manager is the interface by which challenges are loaded and initiated. Once
the Manager has been accepted by the Submission server, the following commands
are recognized:

* &lt;load | send | submit&gt; &lt;challenge_id&gt; &lt;challenge_name&gt;
    * Alert the boss the new challenge is now &lt;challenge_name&gt; with a challenge
      id of &lt;challenge_id&gt;. Note: &lt;challenge_name&gt; must be a challenge in the
      same directory as Manager.py.
* &lt;init&gt;
    * Send out the challenge to all registered participants. Note: there must
      already be a loaded challenge (see above command).
* &lt;ls&gt;
    * List challenges in the current directory.
* &lt;exit | quit&gt;
    * Exit the Manager.

Have Clients Connect
====================

For every participant, supply them with `participant.py` and have them issue the
following:

    $ python3 participant.py [submission_server_ip]

where **submission_server_id** is the IP address of the machine that the
Submission server is running on. If **submission_server_ip** is omitted,
localhost is used.

The participants are then prompted to enter their name and editor. They must
then wait for the Manager to Load up a Challenge.

Load up a Challenge
===================

Issue the &lt;load | send | submit&gt; command from the Manager's prompt with a legal
challenge.

Start the challenge
===================

The Manager can then issue the **init** command and every participant will be
sent the challenge description and will be prompted to accept it. Once all
participants have responded, the Manager can then start the challenge or cancel
it. If the Manager starts the challenge then the challenge will continue until
every participant has either successfully completed it or forfeited.
