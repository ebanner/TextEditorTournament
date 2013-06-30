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

[3) Start [Display web client](#display-web-client-displayindexhtml)](#start-display-web-client)

[4) Start Manager](#start-manager)

[5) Have Participants Connect](#have-participants-connect)

[6) Load up a Challenge](#load-up-a-challenge)

[7) Start the Challenge](#start-the-challenge)

8) Repeat steps 6 through 8

Terminology
===========

### Submission server `server/submission_server.py`

The most important piece of running a tournament. Clients of every type (e.g.
[Manager](Manager-managermanagerpy), Participant, Display) must register with the [Submission server](#submission-server-serversubmission_serverpy). Simply
put, the [Submission server](#submission-server-serversubmission_serverpy) is the brain of the tournament.

### Display server `display/ws.py`

Relays tournament statistics from the [Submission Server](#submission-server-serversubmission_serverpy) 
to the [Display web client](#display-web-client-displayindexhtml).

### [Display web client](#display-web-client-displayindexhtml) `display/index.html` 

Uses WebSockets to establish a connection with the Display server display
tournament statistics it recieves using the HTML5 canvas element.

### Manager `manager/manager.py` 

Interface by which challenges are managed (loaded, initiated, cancelled). The
[Manager](Manager-managermanagerpy) has the following command set:

* **load challenge_id challenge_name**
    * Load up a new challenge named **challenge_name** with a challenge
      id of **challenge_id**. **Note: challenge_name** must be a Challenge.
* **init**
    * Send out the Challenge to all registered participants. Note: there must
      already be a loaded challenge (see above command)
* **ls**
    * List challenges in the current directory
* **quit**
    * Exit the [Manager](Manager-managermanagerpy)

### Participant `participant/participant.py`

Recieves information about Challenges and can accept or reject Challenges that
are presented. If a Participant accepts a challenge, then they must proceed to
work toward completing the Challenge. Once the Participant is confident they
have completed the Challenge correctly, the Participant can then submit the
Challenge to the [Submission server](#submission-server-serversubmission_serverpy). If the Participant completed the Challenge
incorrectly, the Participant will recieve a diff of their work against what the
correct solution.

### Challenge

A directory that resides in the same directory as the [Manager](Manager-managermanagerpy). Within this
directory must be several types of files:

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

The [Submission server](#submission-server-serversubmission_serverpy) by default runs on port 6900.

Start Display Server
====================

Open a terminal, traverse into `display/`, and issue the following command:

    $ python3 ws.py

This Display server listens on port 9999 and assumes the [Submission server](#submission-server-serversubmission_serverpy) is
running on port 6900.

Start [Display web client](#display-web-client-displayindexhtml)
========================

Traverse into `display` and open `index.html` with your favorite web browser.

**Note:** The [Display web client](#display-web-client-displayindexhtml) assumes the Display server is running on the
same machine. In order to run the Display server on another machine, change the
**SERVER_ADDR** value line in `main.js` to the IP address of the machine the
Display server is running on.

Start [Manager](Manager-managermanagerpy)
=============

Open a terminal, traverse into `manager/`, and issue the following command:

    $ python3 manager.py

Have Participants Connect
====================

For every Participant, supply them with `participant.py` and have them issue the
following:

    $ python3 participant.py [submission_server_ip]

where **submission_server_id** is the IP address of the machine that the
[Submission server](#submission-server-serversubmission_serverpy) is running on.
If **submission_server_ip** is omitted, **localhost** is used.

The Participants are then prompted to enter their name and editor. They must
then wait for the [Manager](Manager-managermanagerpy) to Load up a Challenge.

Load up a Challenge
===================

Issue the **load** command from the [Manager](Manager-managermanagerpy)'s prompt with a legal challenge.

Start the Challenge
===================

The [Manager](Manager-managermanagerpy) can then issue the **init** command and every participant will be
sent the challenge description and will be prompted to accept it. Once all
participants have responded, the [Manager](Manager-managermanagerpy) can then start the challenge or cancel
it. If the [Manager](Manager-managermanagerpy) starts the challenge, the challenge will continue until
every participant has either successfully completed it or forfeited.
