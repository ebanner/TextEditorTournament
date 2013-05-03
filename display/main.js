//SERVER_ADDR = "127.0.0.1";
SERVER_ADDR = "137.143.158.1";
SERVER_PORT = 9999;

INSULT_DELAY_INITIAL = 120;
INSULT_DELAY = 60;

/* Contains the visual display data:
 *  Creates a websocket client that receives real-time updates from the server
 *  and displays them, along with audio playback.
 */


// Participant object (struct):
function Participant(participant, editor){
    // Name and editor of choice.
    this.participant = participant;
    this.editor = editor;
    
    // Flagged TRUE if this participant accepts a challenge.
    this.accepted = false;
}


// GLOBAL CONSTANTS
var NOTIFICATION_TYPE_NORMAL = 0;
var NOTIFICATION_TYPE_GOOD = 1;
var NOTIFICATION_TYPE_BAD = 2;
var NOTIFICATION_TYPE_SYS = 3;
var NOTIFICATION_TYPE_ALERT = 4;
var NOTIFICATION_TYPE_ERROR = 5;

// PROTOCOL STATE CONSTANTS
var PROTOCOL_STANDBY = 0; // waiting for instruction
var PROTOCOL_ADD_PARTICIPANT_name = 10; // waiting for add name
var PROTOCOL_ADD_PARTICIPANT_editor = 11; // waiting for add editor
var PROTOCOL_REMOVE_PARTICIPANT = 20; // waiting for remove name
var PROTOCOL_INIT_CHALLENGE_id = 30; // waiting for init challenge id
var PROTOCOL_INIT_CHALLENGE_name = 31; // waiting for init challenge name
var PROTOCOL_INIT_CHALLENGE_dlen = 32; // waiting for init description len
var PROTOCOL_INIT_CHALLENGE_desc = 33; // waiting for init description
var PROTOCOL_PARTICIPANT_ACCEPTED = 40; // waiting for accepted name
var PROTOCOL_START_CHALLENGE = 90; // waiting for accepted name
var PROTOCOL_CANCEL_CHALLENGE = 91; // waiting for accepted name
var PROTOCOL_SET_PARTICIPANT_STATUS_name = 101; // waiting for status name
var PROTOCOL_SET_PARTICIPANT_STATUS_type = 102; // waiting for status type
var PROTOCOL_INCORRECT_SUBMISSION = 110; // waiting for participant name
var PROTOCOL_RECV_EDITOR_STATUS_editor = 201; // waiting to receive editor name
var PROTOCOL_RECV_EDITOR_STATUS_time = 202; // waiting to receive editor time
var PROTOCOL_RECV_PARTICIPANT_STATUS_name = 210; //
var PROTOCOL_RECV_PARTICIPANT_STATUS_editor = 211; //
var PROTOCOL_RECV_PARTICIPANT_STATUS_time = 212; //
var PROTOCOL_RECV_AVERAGE_TIME = 220; //

// Protocol temporaries (used for multi-step protocol events):
var PROTOCOL_TEMP_editor;
var PROTOCOL_TEMP_name;
var PROTOCOL_TEMP_id;
var PROTOCOL_TEMP_dlen;
var PROTOCOL_TEMP_curline;
var PROTOCOL_TEMP_dlines;

// Current protocol state:
var protocolState = PROTOCOL_STANDBY;

// GLOBAL APP VARIABLES:
var ws = false; // websocket (initially FALSE to imply it is not connected)
var display; // current Display object
var FPS = 30; // frames per second
var dT = Math.floor(1000/FPS); // delta time (between frames)

// SOUND OBJECTS
var acceptSound = new Audio("audio/pop.wav");
acceptSound.load();
var startSound = new Audio("audio/airhorn.wav");
startSound.load();
var finishedSound = new Audio("audio/finished.wav");
finishedSound.load();
var forfeitSound = new Audio("audio/forfeit.wav");
forfeitSound.load();
var wrongSound = new Audio("audio/wrong.wav");
wrongSound.load();
var errorSound = new Audio("audio/error.wav");
errorSound.load();

// MUSIC SOUNDS
var battleMusic = new Array();
var battleMusic1 = new Audio("audio/battle_music_1.mp3");
battleMusic1.load();
battleMusic.push(battleMusic1);
var battleMusic2 = new Audio("audio/battle_music_2.mp3");
battleMusic2.load();
battleMusic.push(battleMusic2);
var curBattleMusic = false;

var talkSound = false;

// PARTICIPANT LISTS
var activeParticipants = new Array();
var numFinished = 0;


// Initialize the websocket (try to connect to the WS server) using the given
//  IP address and port number. If WebSockets are not supported, or it is
//  already connected, returns FALSE. Otherwise, returns TRUE.
function initWebSocket(ip, port){
    // if websockets are not supported, report error and exit
    if(!("WebSocket" in window)){
        notify("WebSockets are not supported by this browser.",
            NOTIFICATION_TYPE_ERROR);
        return false;
    }
    
    // if the websocket is already connected, report error and exit
    if(ws){
        alert("WebSocket already connected.",
            NOTIFICATION_TYPE_ERROR);
        return false;
    }
    
    // Create a new websocket, and connect it to the server.
    ws = new WebSocket("ws://" + ip + ":" + port + "/text_editing_tournament",
        ['text_editing_tournament']);
    
    // When socket is open, send greetings message and notify connected.
    ws.onopen = function(){
        ws.send("TEXT_EDITOR_TOURNAMENT_TYPE_DISPLAY");
        notify("Connected to server.", NOTIFICATION_TYPE_SYS);
    };
    
    // If socket experiences an error, display the error message.
    ws.onerror = function(error) {
        notify("The WebSocket has experienced an error.",
            NOTIFICATION_TYPE_ERROR);
        protocolState = PROTOCOL_STANDBY;
        //console.log('WebSocket Error ' + error); TODO - what?
    };
    
    // If socket is closed, display notification alert, and set ws to false
    //  to indicate that it is no longer connected.
    ws.onclose = function(){
        notify("Disconnected from server.", NOTIFICATION_TYPE_ALERT);
        errorSound.play();
        protocolState = PROTOCOL_STANDBY;
        ws = false;
    }
    
    // Parse any messages that the server sends.
    ws.onmessage = function(e){
        parseServerMessage(e.data);
    };
    
    return true;
}


// When document is loaded, initialize the websocket, add a listener to the
//  input box, and zero-out all of the text values that may have been cached
//  from before.
$(document).ready(function(){
    // Check if audio is supported in this browser. If not, alert the message.
    var audioTagSupport = !!(document.createElement('audio').canPlayType);
    if (!audioTagSupport){
        notify("Audio playback is not supported by this browser.",
            NOTIFICATION_TYPE_ALERT);
    }
    
    // Try to initialize the websocket here.
    var retval = initWebSocket(SERVER_ADDR, SERVER_PORT);
    //alert(retval);
    
    // Start the canvas animator
    display = new DisplayWelcomeMode();
    /*display = new DisplayChallengeMode("0", "Test Challenge");
    display.challengeName = "Hi";
    display.addCompetitor("person1", "vim")
    display.addCompetitor("person2", "something else")
    display.addCompetitor("person3", "gedit")*/
    
    setTimeout(updateFrame, dT);
});


// Makes the canvas go into fullscreen mode. NOTE: this does not change
//  the canvas resolution, just expands the image to fit the screen.
function goFullScreen(){
    display.goFullScreen();
}


// Returns the number of frames in the given number of seconds, based on
//  the current FPS value (frames per second).
function secondsToFrames(seconds){
    return seconds * FPS;
}


// Called each frame (via Javascript events) to re-draw the entire canvas
//  and refresh it for the next frame.
function updateFrame(){
    display.update();
    setTimeout(updateFrame, dT);
}


// Parse a message received from the server through the websocket.
function parseServerMessage(data){
    // if protocol is in standby mode, check for new instruction
    if(protocolState == PROTOCOL_STANDBY){
        if(data == "ADD_PARTICIPANT") // go to add participant mode
            protocolState = PROTOCOL_ADD_PARTICIPANT_name;
        
        else if(data == "REMOVE_PARTICIPANT") // go to remove participant mode
            protocolState = PROTOCOL_REMOVE_PARTICIPANT;
        
        /*** CHALLENGE INIT HEADERS ***/
        
        else if(data == "CHALLENGE_INITIATE")
            protocolState = PROTOCOL_INIT_CHALLENGE_id;
        
        else if(data == "PARTICIPANT_ACCEPTED")
            protocolState = PROTOCOL_PARTICIPANT_ACCEPTED;
        
        // if challenge start received, load challenge display
        else if(data == "CHALLENGE_START"){
            startSound.play();
            
            // play a random battle music clip
            var index = Math.floor(Math.random() * battleMusic.length);
        	curBattleMusic = battleMusic[index];
        	curBattleMusic.loop = true;
        	curBattleMusic.volume = 0.5;
        	curBattleMusic.play();
			
            numFinished = 0; // number done initially at none
            var challengeId = display.challengeId
            var challengeName = display.challengeName;
            display = new DisplayChallengeMode(challengeId, challengeName);
            // find each accepting challenger; if found, add him/her and
            //  their respective editor to the list.
            for(var i=0; i<activeParticipants.length; i++){
                if(activeParticipants[i].accepted)
                    display.addCompetitor(
                        activeParticipants[i].participant,
                        activeParticipants[i].editor);
                activeParticipants[i].accepted = false;
            }
        }
        
        // if challenge cancelled, load welcome display
        else if(data == "CHALLENGE_CANCEL")
            display = new DisplayWelcomeMode();
        
        /*** CHALLENGE MODE HEADERS ***/
        
        else if(data == "SET_PARTICIPANT_STATUS") // go to set status mode
            protocolState = PROTOCOL_SET_PARTICIPANT_STATUS_name;
        
        else if(data == "INCORRECT_SUBMISSION") // go to wrong submission mode
            protocolState = PROTOCOL_INCORRECT_SUBMISSION;
        
        else if(data == "CHALLENGE_FINISH"){
            display = new DisplayStatsMode();
            // stop playing the music
            if(curBattleMusic){
            	curBattleMusic.pause();
            	curBattleMusic = false;
        	}
            protocolState = PROTOCOL_RECV_EDITOR_STATUS_editor;
        }
    }
    
    /*** RECEIVE EDITOR TIME STATS ***/
    
    // if protocol is in receive editor status mode and waiting for editor
    else if(protocolState == PROTOCOL_RECV_EDITOR_STATUS_editor){
        if(data == "MINIMUM_EDITOR_TIMES_STATISTIC_END"){
            protocolState = PROTOCOL_RECV_PARTICIPANT_STATUS_name;
        }
        else{
            PROTOCOL_TEMP_editor = data;
            protocolState = PROTOCOL_RECV_EDITOR_STATUS_time;
        }
    }
    
    // if protocol is in receive editor status mode and waiting for time
    else if(protocolState == PROTOCOL_RECV_EDITOR_STATUS_time){
        display.addEditorTime(PROTOCOL_TEMP_editor, data);
        protocolState = PROTOCOL_RECV_EDITOR_STATUS_editor;
    }
    
    /*** RECEIVE PARTICIPANT TIME STATS ***/
    
    // if protocol is in receive participant status and waiting for name
    else if(protocolState == PROTOCOL_RECV_PARTICIPANT_STATUS_name){
        if(data == "INDIVIDUAL_PARTICIPANT_STATISTICS_END"){
            protocolState = PROTOCOL_RECV_AVERAGE_TIME;
        }
        else{
            PROTOCOL_TEMP_name = data;
            protocolState = PROTOCOL_RECV_PARTICIPANT_STATUS_editor;
        }
    }
    
    // if protocol is in receive participant status and waiting for editor
    else if(protocolState == PROTOCOL_RECV_PARTICIPANT_STATUS_editor){
        PROTOCOL_TEMP_editor = data;
        protocolState = PROTOCOL_RECV_PARTICIPANT_STATUS_time;
    }
    
    // if protocol is in receive participant status and waiting for time
    else if(protocolState == PROTOCOL_RECV_PARTICIPANT_STATUS_time){
        display.addParticipantTime(
            PROTOCOL_TEMP_name, PROTOCOL_TEMP_editor, data);
        protocolState = PROTOCOL_RECV_PARTICIPANT_STATUS_name;
    }
    
    /*** RECEIVE AVERAGE TIME VALUE ***/
    
    // if protocol is in receive average time mode and waiting for time
    else if(protocolState == PROTOCOL_RECV_AVERAGE_TIME){
        display.setAverageTime(data);
        // announce best and worst editor
        if(display.editorTimes.length >= 1){
			var words =
				"" + display.editorTimes[0][0] + " wins this challenge. " +
				"" + display.editorTimes[display.editorTimes.length-1][0] +
				" sucks.";
			playText(words);
		}
        protocolState = PROTOCOL_STANDBY;
    }
    
    
    /*** ADD AND REMOVE PARTICIPANT STATES ***/
    
    // if protocol is in add participant mode and waiting for name:
    else if(protocolState == PROTOCOL_ADD_PARTICIPANT_name){
        PROTOCOL_TEMP_name = data;
        protocolState = PROTOCOL_ADD_PARTICIPANT_editor;
    }
    
    // if protocol is in add participant mode and waiting for editor:
    else if(protocolState == PROTOCOL_ADD_PARTICIPANT_editor){
        var participant = new Participant(PROTOCOL_TEMP_name, data);
        activeParticipants.push(participant);
        protocolState = PROTOCOL_STANDBY;
    }
    
    // if protocol is in remove participant mode and waiting for name:
    else if(protocolState == PROTOCOL_REMOVE_PARTICIPANT){
        // search the list to remove the participant of the sent name
        for(var i=0; i<activeParticipants.length; i++){
            if(activeParticipants.participant == data)
                activeParticipants.splice(i, 1);
        }
        protocolState = PROTOCOL_STANDBY;
    }
    
    /*** CHALLENGE INITIATE STATES ***/
    
    // if protocol is in init challenge mode and waiting for id:
    else if(protocolState == PROTOCOL_INIT_CHALLENGE_id){
        PROTOCOL_TEMP_id = data;
        protocolState = PROTOCOL_INIT_CHALLENGE_name;
    }
    
    // if protocol is in init challenge mode and waiting for name:
    else if(protocolState == PROTOCOL_INIT_CHALLENGE_name){
        PROTOCOL_TEMP_name = data;
        protocolState = PROTOCOL_INIT_CHALLENGE_dlen;
    }
    
    // if protocol is in init challenge mode and waiting for description len:
    else if(protocolState == PROTOCOL_INIT_CHALLENGE_dlen){
        PROTOCOL_TEMP_dlen = data;
        PROTOCOL_TEMP_dlines = new Array();
        PROTOCOL_TEMP_curline = 0;
        protocolState = PROTOCOL_INIT_CHALLENGE_desc;
    }
    
    // while protocol is in init description read mode:
    else if(protocolState == PROTOCOL_INIT_CHALLENGE_desc){
        // add the lines one by one
        PROTOCOL_TEMP_dlines.push(data);
        PROTOCOL_TEMP_curline++;
        // if all lines have been read, go into init mode, and set the
        //  screen to challenge init display with the appropriate data.
        if(PROTOCOL_TEMP_curline >= PROTOCOL_TEMP_dlen){
            display = new DisplayInitMode(
                PROTOCOL_TEMP_id, PROTOCOL_TEMP_name, PROTOCOL_TEMP_dlines);
            playText("Challenge " + PROTOCOL_TEMP_id + " initiated.");
            protocolState = PROTOCOL_STANDBY;
        }
    }
    
    // if protocol is in get participant accepted state waiting for name:
    else if(protocolState == PROTOCOL_PARTICIPANT_ACCEPTED){
        // find the active participant that the name matches to
        for(var i=0; i<activeParticipants.length; i++){
            if(activeParticipants[i].participant == data){
                activeParticipants[i].accepted = true;
                display.addAcceptingParticipant(data);
                acceptSound.play();
                break;
            }
        }
        protocolState = PROTOCOL_STANDBY;
    }
    
    /*** CHALLENGE MODE STATES ***/
    
    // if protocol is in set status mode and waiting for name:
    else if(protocolState == PROTOCOL_SET_PARTICIPANT_STATUS_name){
        PROTOCOL_TEMP_name = data;
        protocolState = PROTOCOL_SET_PARTICIPANT_STATUS_type;
    }
    
    // if protocol is in set status mode and waiting for status type:
    else if(protocolState == PROTOCOL_SET_PARTICIPANT_STATUS_type){
        var retvals = display.getCompetitor(PROTOCOL_TEMP_name);
        var competitor = retvals[0];
        var index = retvals[1];
        //display.onTime = function() {}; // empty out onTime function
        if(competitor){
            switch(data){
                case "STATUS_WORKING":
                    competitor.status = PARTICIPANT_WORKING;
                    break;
                case "STATUS_FINISHED":
                    competitor.status = PARTICIPANT_FINISHED;
                    notify("" + PROTOCOL_TEMP_name + " finished!",
                        NOTIFICATION_TYPE_GOOD);
                    finishedSound.play();
                    // if first one to finish, play "first done" text
                    numFinished++;
                    if(numFinished == 1)
                        playText("First submission by " + competitor.participant
                            + " representing " + competitor.editor);
                    
                    // set the correct placement in the challenge, and swap the
                    //  finished competitor's placement in the array with
                    //  whichever competitor is actually in that position now.
                    competitor.finishedPlace = numFinished;
                    display.competitors[index] = display.competitors[numFinished-1];
                    display.competitors[numFinished-1] = competitor;
                    break;
                case "STATUS_FORFEIT":
                    competitor.status = PARTICIPANT_FORFEIT;
                    notify("" + PROTOCOL_TEMP_name + " gave up.",
                        NOTIFICATION_TYPE_BAD);
                    forfeitSound.play();
                    playText("" + competitor.participant + " gave up. " +
                        "That's because " + competitor.editor + " sucks.");
                    break;
                default:
                    break;
            }
        }
        protocolState = PROTOCOL_STANDBY;
    }
    
    // if protocol is in incorrect submission mode and waiting for user name.
    else if(protocolState == PROTOCOL_INCORRECT_SUBMISSION){
        notify("" + data + " was incorrect.", NOTIFICATION_TYPE_ALERT);
        wrongSound.play();
        playText("" + data + ", your submission was incorrect.");
        protocolState = PROTOCOL_STANDBY;
    }
}

// Display a notification bubble on the screen that will show the given
//  text for a while, and then fade out.
// PARAMETERS:  text: the text to be displayed
//              type: depending on the given type, the color of the text/bubble
//                  will varry.
function notify(text, type){
    var colorStr = "#FFFFFF";
    switch(type){
        case NOTIFICATION_TYPE_SYS:
        case NOTIFICATION_TYPE_GOOD:
            colorStr = "#00FF00"; // green
            break;
        case NOTIFICATION_TYPE_ALERT:
            colorStr = "#FFFF00"; // yellow
            break;
        case NOTIFICATION_TYPE_ERROR:
        case NOTIFICATION_TYPE_BAD:
            colorStr = "#FF0000"; // red
            break;
        case NOTIFICATION_TYPE_NORMAL:
        default:
            break; // white
    }
    display.addMessage(text, colorStr);
}


// list of "hurry up" comments (tuples; participant's name is added in middle.
var longWaitComments = new Array();
longWaitComments.push([
    "Hurry up, ",
    ". Any day now."]);
longWaitComments.push([
    "",
    ", are you writing by hand? What's taking so long?"]);
longWaitComments.push([
    "",
    ", this is a competition. The point is to be quick."]);
longWaitComments.push([
    "By all means, take your time ",
    ". It's not like we have anywhere better to be."]);
longWaitComments.push([
    "If this was a competition for the worst editor, I bet ",
    " would win."]);
longWaitComments.push([
    "Almost done there, ",
    "?"]);
longWaitComments.push([
    "What's taking so long, ",
    "? I'm about to fall into sleep mode."]);
longWaitComments.push([
    "I've seen glaciers type faster than you, ",
    ""]);
longWaitComments.push([
    "",
    ", these computers are getting replaced in a few months. " +
        "Please finish before then."]);
longWaitComments.push([
    "The lightbulb on this projector only has so many hours of life, ",
    "."]);
longWaitComments.push([
    "I've seen paint dry faster than you type, ",
    "."]);
longWaitComments.push([
    "Error: null pointer exception in ",
    "'s brain."]);
longWaitComments.push([
    "",
    ", if you keep this up, I'm going to uninstall your editor from all " +
        "computers in the UNIX lab."]);
longWaitComments.push([
    "I can see this challenge was clearly not designed for amateurs, ",
    "."]);
longWaitComments.push([
    "Please, ",
    ", use a better editor next time. Perhaps Notepad."]);
longWaitComments.push([
    "You've hit a new record, ",
    ". Your words per minute are now 0 point 0 0 0 0 0 0 0 0 0. 3."]);
longWaitComments.push([
    "I would cut you some slack, ",
    ", but paper jams were obsolete for the past 40 years."]);
longWaitComments.push([
    "Your method for this challenge reminds me of the Ostrich algorithm, ",
    ""]);
longWaitComments.push([
    "",
    ", I can read and write to a disk faster than you type."]);
longWaitComments.push([
    "",
    ", I've done extensive analysis on your typing runtime. It's exponential."]);
longWaitComments.push([
    "I can probably solve the halting problem before you finish this challenge, ",
    ""]);
longWaitComments.push([
    "",
    ", you are like a process currently requesting a resource: faster typing speed. " +
        "Unfortunately, it's currently being occupied by every other participant."]);
longWaitComments.push([
    "",
    ", you are like the Bubble sort of typing."]);
longWaitComments.push([
    "This challenge isn't exaclty N P complete, ",
    ""]);
longWaitComments.push([
    "",
    ", this is Richard Stallman. Stop eating my foot."]);
longWaitComments.push([
    "",
    " extends class Typing implements interface Slow."]);
longWaitComments.push([
    "",
    ", the only way you can win the challenge now is if you D-DOS me."]);
longWaitComments.push([
    "",
    ", your typing speed can use some optimization."]);
longWaitComments.push([
    "",
    "Clearly, you're having as hard of a time with this challenge as you would "
        + "with the Art of Programming books."]);
longWaitComments.push([
    "Dear ",
    ", you're a horrible person. Sincerily, Linus Torvalds."]);
longWaitComments.push([
    "I've seen infinite loops finish faster than you, ",
    ""]);
    
// randomly choose a starting index
var longWaitCommentIndex = Math.floor(Math.random() * longWaitComments.length);

// Randomly plays a text-to-speech message to indicate that the given
//  participant is taking too long.
function announceLongWait(participant) {
    var comment = longWaitComments[longWaitCommentIndex];
    var words = "" + comment[0] + participant + comment[1];
    if(words.length > 100 || Math.random() < 0.5) // play with male voice
        playText2(words);
    else // play with Google voice
        playText(words);
    longWaitCommentIndex++;
    if(longWaitCommentIndex >= longWaitComments.length)
        longWaitCommentIndex = 0;
}


// Queries Google Translate text-to-speech API to playback the given text.
//  NOTE: currently, this does not work on Firefox.    
function playText(text){
    if (text == "")
        return false;
    
    // pause audio if it's playing
    if(talkSound && !talkSound.paused)
    	talkSound.pause();
	
    talkSound = new Audio();
    talkSound.src =
        "http://translate.google.com/translate_tts?tl=en&q="
        //"http://speechutil.com/convert/ogg?text=%27"
        + encodeURIComponent(text);// + "%27";
    talkSound.load();
    talkSound.play();
}

// Queries Google Translate text-to-speech API to playback the given text.
//  NOTE: currently, this does not work on Firefox.    
function playText2(text){
    if (text == "")
        return false;
    
    // pause audio if it's playing
    if(talkSound && !talkSound.paused)
    	talkSound.pause();
	
	talkSound = new Audio();
    talkSound.src =
        //"http://translate.google.com/translate_tts?tl=en&q="
        "http://speechutil.com/convert/ogg?text=%27"
        + encodeURIComponent(text) + "%27";
    talkSound.load();
    talkSound.play();
}
