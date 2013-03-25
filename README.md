# Text-Editing Tournament

Client and Submission server code for judging submissions for the 2013 SUNY Potsdam Text-Editing Tournament.

To use this software, it is recommended `client.py` and `server.py` are in
their own separate directories.

The first step is to start up the server like so:

    cd server/
    ./submission_server.py

Once the client is ready to submit a file `foo`, issue the following commands:

    cd client/
    ./client foo

The server will then check its current directory for a file `foo.sol` and diff
it with the submitted `foo` file. The server will then print some basic
information to stdout like participant name, editor, filename, and time. This
information is logged along with a diff of the user's submission against the
solution file in the file `foo.log`.

# Protocol for sending files

In order for a client to send a file `foo` for submission, there needs to be a
file named `info.txt` in the client's current directory.  The only pieces of
information that need to be in this file are the client's name and editor
separated by a newline. Here is an example `info.txt` file:

    $ cat info.txt
    Edward Banner
    Vim

Assuming both `foo` and `info.txt` exist in the client's current directory, the
following information gets sent to the server in this order:

* The name of the participant followed by a newline.
* The name of the participant's editor followed by a newline.
* The name of the file being submitted by the participant followed by a newline.
* The size of the submission file in bytes.
* The file itself.

Example usage:

    cd server/
    ./submission_server.py

    cd client/
    ./client.py move_lines
    ./client.py move_lines
    ./client.py move_lines
    ./client.py move_lines
    ./client.py move_lines

Example server output:
    
    Participant: Edward Banner
    Editor: Vim
    Name of file: move_lines
    Number of bytes: 55
    7.083601474761963

    Participant: Edward Banner
    Editor: Vim
    Name of file: move_lines
    Number of bytes: 55
    8.956053733825684

    Participant: Edward Banner
    Editor: Vim
    Name of file: move_lines
    Number of bytes: 73
    19.141838312149048

    Participant: Edward Banner
    Editor: Vim
    Name of file: move_lines
    Number of bytes: 55
    29.168554544448853

    Participant: Edward Banner
    Editor: Vim
    Name of file: move_lines
    Number of bytes: 55
    38.04445934295654

    ^C Tearing down the server...

Example log file:

    Edward Banner
    Vim
    7.083444833755493

    Edward Banner
    Vim
    8.955938339233398

    Edward Banner
    Vim
    --- move_lines
    +++ move_lines.sol
    @@ -1,5 +1,3 @@
    Lorem ipsum is a cool guy.
 
    Cool guy is a lorem ipsum.
    -
    -Oh the humanity!
    19.141724586486816

    Edward Banner
    Vim
    --- move_lines
    +++ move_lines.sol
    @@ -1,3 +1,3 @@
    Lorem ipsum is a cool guy.
 
    -Cool is a lorem guy ipsum.
    +Cool guy is a lorem ipsum.
    29.168437480926514

    Edward Banner
    Vim
    38.044344425201416
