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
var PROTOCOL_RECV_STATUS = 201; // waiting to receive status info

// Protocol temporaries (used for multi-step protocol events):
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

// PARTICIPANT LISTS
var activeParticipants = new Array();


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
    var retval = initWebSocket("127.0.0.1", 9999);
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
            display = DisplayStatsMode();
            protocolState = PROTOCOL_RECV_STATUS;
        }
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
                    break;
                default:
                    break;
            }
        }
        protocolState = PROTOCOL_STANDBY;
    }
    
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
    //playText(text);
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


// Queries Google Translate text-to-speech API to playback the given text.
//  NOTE: currently, this does not work on Firefox.    
function playText(text){
    if (text == "")
        return false;
    
    var audio = new Audio();//document.createElement("audio");
    //audio.setAttribute("src",
    audio.src =
        //"http://translate.google.com/translate_tts?tl=en&q="
        "http://speechutil.com/convert/ogg?text=%27"
        + encodeURIComponent(text) + "%27";
    audio.load();
    audio.play();
}
