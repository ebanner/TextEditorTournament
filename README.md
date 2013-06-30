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

[1) Start Submission server](#start-submission-server)

[2) Start Display server](#start-display-server)

[3) Start Display web client](#start-display-web-client)

[4) Start Manager](#start-manager)

[5) Have Participants Connect](#have-participants-connect)

[6) Load up a Challenge](#load-up-a-challenge)

[7) Start the Challenge](#start-the-challenge)

8) Repeat steps 6 through 8

Terminology
===========

### Submission server

The most important piece of running a tournament is the Submission server.
Clients of every type (e.g. Manager, participants, display) must register with
the Submission server. Simply put, the Submission Server is the brain of the
tournament.

### Display server

The Display server realays tournament statistics from the Submission server to
the Display web client.

### Display web client

The Display web client uses WebSockets to establish a connection with and
display tournament statistics it recieves from the Display server using the
HTML5 canvas element.

### Manager

The Manager is the interface by which challenges are managed (loaded, initiated,
cancelled). The Manager has the following command set:

* **load challenge_id challenge_name**
    * Alert the boss the new challenge is now **challenge_name** with a challenge
      id of **challenge_id**. Note: **challenge_name** must be a challenge in the
      same directory as Manager.py.
* **init**
    * Send out the challenge to all registered participants. Note: there must
      already be a loaded challenge (see above command).
* **ls**
    * List challenges in the current directory.
* **quit**
    * Exit the Manager.

### Participant

A Participant recieves information about challenges and can accept or reject
challenges that are presented. If a Participant accepts a challenge, then they
must proceed to work toward completing the challenge. Once the Participant is
confident they have completed the challenge correctly, the Participant can then
submit the challenge to the Submission server. If the Participant completed the
challenge incorrectly, the Participant will recieve a diff of their work against
what the correct solution.

### Challenge

A Challenge is a directory that resides in the same directory as the Manager.
Within this directory must be several types of files:

* A Description File
    * A file named `description.info`. The format of this file is as follows:
        * The first line is the name of the challenge
        * The second line contains a newline
        * The rest of the file contains a description of the challenge and
          optionally an example
* Challenge Files
    * These files are the text files that will be sent over to Participants at
      the beginning of a challenge
* Solution Files
    * These files have a `.sol` extension and are the files that the challenge
      files will be diffed against. There must exist a bijection amongst
      Challenge Files and Solution Files (e.g. If `foo` is a Challenge File,
      then there must exist a Solution File by the name of `foo.sol`)

Start Submission Server
=======================

Open a terminal, traverse into `server/`, and issuing the following command:

    $ python3 submission_server.py

The submission server by default runs on port 6900.

Start Display Server
====================

Open a terminal, traverse into `display/`, and issue the following command:

    $ python3 ws.py

This Display server listens on port 9999 and assumes the Submission server is
running on port 6900.

Start Display web client
========================

Traverse into `display` and open `index.html` with your favorite web browser.

**Note:** The Display web client assumes the Display server is running on the
same machine. In order to run the Display server on another machine, change the
**SERVER_ADDR** value line in `main.js` to the IP address of the machine the
Display server is running on.

Start Manager
=============

Open a terminal, traverse into `manager/`, and issue the following command:

    $ python3 manager.py

Have Clients Connect
====================

For every Participant, supply them with `participant.py` and have them issue the
following:

    $ python3 participant.py [submission_server_ip]

where **submission_server_id** is the IP address of the machine that the
Submission server is running on. If **submission_server_ip** is omitted,
**localhost** is used.

The Participants are then prompted to enter their name and editor. They must
then wait for the Manager to Load up a Challenge.

Load up a Challenge
===================

Issue the **load** command from the Manager's prompt with a legal challenge.

Start the Challenge
===================

The Manager can then issue the **init** command and every participant will be
sent the challenge description and will be prompted to accept it. Once all
participants have responded, the Manager can then start the challenge or cancel
it. If the Manager starts the challenge, the challenge will continue until
every participant has either successfully completed it or forfeited.
