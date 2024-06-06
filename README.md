Text Editor Tournament
=======================

<a href="http://www.youtube.com/watch?feature=player_embedded&v=7cm5bPccSeg" target="_blank">
  <img src="http://img.youtube.com/vi/7cm5bPccSeg/0.jpg" alt="Text Editor Tournament" width="240" height="180" border="10" />
</a>

![Text Editor Tournament in Action](https://raw.github.com/ebanner/text-editing-tournament/master/screenshot/TET.png "Screenshot")

Client-server system connecting together multiple tournament participants, a
Manager (administrator), and a web-based display frontend system through a
central server.

The server handles distributing challenges submitted by the Manager and
submissions of answers by the participants. The server and client programs are
written in Python 3. The web-based frontend displays information about the
tournament in real-time using the HTML5 canvas and WebSockets.

Table of Contents
=================

* [Terminology](#terminology)
    * [Submission server](#submission-server-serversubmission_serverpy)
    * [Display](#display-server-displaywspy)
    * [Display web client](#display-web-client-displayindexhtml)
    * [Manager](#manager-managermanagerpy)
    * [Participant](#participant-participantparticipantpy)
    * [Challenge](#challenge)

* [Normal Tournament sequence](#normal-tournament-sequence)
    * [Start Submission server](#start-submission-server)
    * [Start Display server](#start-display-server)
    * [Start Display web client](#start-display-web-client)
    * [Start Manager](#start-manager)
    * [Have Participants connect](#have-participants-connect)
    * [Load up a Challenge](#load-up-a-challenge)
    * [Start the Challenge](#start-the-challenge)
    * Repeat steps 6 through 8

* [Other](#other)
    * [Videos](#video)
    * [Screenshots](#screenshots)


Terminology
===========

#### Submission server `server/submission_server.py`

The most important piece of running a tournament. Clients of every type (e.g.
[Manager](#manager-managermanagerpy),
[Participant](#participant-participantparticipantpy),
[Display](#display-server-displaywspy) must register with the [Submission
server](#submission-server-serversubmission_serverpy). Simply put, the
[Submission server](#submission-server-serversubmission_serverpy) is the brain
of the tournament.

#### Display server `display/ws.py`

Relays tournament statistics from the [Submission
Server](#submission-server-serversubmission_serverpy) to the [Display web
client](#display-web-client-displayindexhtml).

#### Display web client `display/index.html` 

Uses WebSockets to establish a connection with the [Display
server](#display-server-displaywspy) to display tournament statistics it
recieves. The HTML5 canvas element is used for displaying graphics.

#### Manager `manager/manager.py` 

Interface by which [Challenges](#challenge) are managed (loaded, initiated,
cancelled). The [Manager](#manager-managermanagerpy) has the following command
set:

* **load challenge_id challenge_name**
    * Sets the current [Challenge](#challenge) to **challenge_name** with a
      challenge ID of **challenge_id**.
* **init**
    * Send out the current [Challenge](#challenge) to all registered
      [Participants](#participant-participantparticipantpy).
* **ls**
    * List [Challenges](#challenge) in the current directory
* **quit**
    * Exit the [Manager](#manager-managermanagerpy)

#### Participant `participant/participant.py`

Recieves information about [Challenges](#challenge) and can accept or reject
[Challenges](#challenge) that are presented. If a
[Participant](#participant-participantparticipantpy) accepts a challenge, then
they must proceed to work toward completing the [Challenge](#challenge). Once
the [Participant](#participant-participantparticipantpy) is confident they have
completed the [Challenge](#challenge) correctly, the
[Participant](#participant-participantparticipantpy) can then submit the
[Challenge](#challenge) to the [Submission
server](#submission-server-serversubmission_serverpy). If the
[Participant](#participant-participantparticipantpy) answered the
[Challenge](#challenge) incorrectly, the
[Participant](#participant-participantparticipantpy) will recieve a diff of
their work against what the correct solution.

#### Challenge

A directory that resides in the same directory as the
[Manager](#manager-managermanagerpy). Within this directory must be several
types of files:

* Description File
    * A file named `description.info`. The format of this file is as follows:
        * The first line is the name of the challenge
        * The second line is blank
        * The rest of the file contains a description of the challenge
* Challenge Files
    * Files that will be sent over to
      [Participants](#participant-participantparticipantpy) at the beginning of
      a challenge
* Solution Files
    * These files have a `.sol` extension. Challenge Files will be diffed
      against these. There must exist a bijection amongst Challenge Files and
      Solution Files (e.g. If `foo` is a Challenge File, then there must exist a
      Solution File by the name of `foo.sol`)


Normal Tournament sequence
==========================

### Start Submission Server

Open a terminal, traverse into `server/`, and issuing the following command:

    $ python3 submission_server.py

The [Submission server](#submission-server-serversubmission_serverpy) by default
runs on port 6900.

### Start Display Server

Open a terminal, traverse into `display/`, and issue the following command:

    $ python3 ws.py

This [Display server](#display-server-displaywspy) runs on port 9999 and
assumes the [Submission server](#submission-server-serversubmission_serverpy) is
running on port 6900.

### Start Display web client

Traverse into `display/` and open `index.html` with your favorite web browser.

**Note:** The [Display web client](#display-web-client-displayindexhtml) assumes
the [Display server](#display-server-displaywspy) is running on the same
machine. In order to run the [Display server](#display-server-displaywspy) on
another machine, change the **SERVER_ADDR** value line in `main.js` to the IP
address of the machine the [Display server](#display-server-displaywspy) is
running on.

### Start Manager

Open a terminal, traverse into `manager/`, and issue the following command:

    $ python3 manager.py

### Have Participants connect

For every [Participant](#participant-participantparticipantpy), supply them with
`participant.py` and have them issue the following:

    $ python3 participant.py [submission_server_ip]

where **submission_server_id** is the IP address of the machine that the
[Submission server](#submission-server-serversubmission_serverpy) is running on.
If **submission_server_ip** is omitted, **localhost** is used.

The [Participants](#participant-participantparticipantpy) are then prompted to
enter their name and editor. They must then wait for the
[Manager](#manager-managermanagerpy) to Load up a [Challenge](#challenge).

### Load up a Challenge

Issue the **load** command from the [Manager](#manager-managermanagerpy)'s
prompt with a legal [Challenge](#challenge).

### Start the Challenge

The [Manager](#manager-managermanagerpy) can then issue the **init** command and
every [Participant](#participant-participantparticipantpy) will be sent the
challenge description and will be prompted to accept it. Once all
[Participants](#participant-participantparticipantpy) have responded, the
[Manager](#manager-managermanagerpy) can then start the challenge or cancel it.
If the [Manager](#manager-managermanagerpy) starts the challenge, the challenge
will continue until every [Participant](#participant-participantparticipantpy)
has either successfully completed it or forfeited.
