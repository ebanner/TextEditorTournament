/* Contains the visual display data:
 *  Creates a websocket client that receives real-time updates from the server
 *  and displays them, along with audio playback.
 */


// GLOBAL CONSTANTS
var NOTIFICATION_TYPE_NORMAL = 0;
var NOTIFICATION_TYPE_GOOD = 1;
var NOTIFICATION_TYPE_BAD = 2;
var NOTIFICATION_TYPE_SYS = 3;
var NOTIFICATION_TYPE_ALERT = 4;
var NOTIFICATION_TYPE_ERROR = 5;

// PROTOCOL STATE CONSTANTS
var PROTOCOL_STANDBY = 0; // waiting for instruction
var PROTOCOL_ADD_PARTICIPANT_name = 1; // waiting for add name
var PROTOCOL_ADD_PARTICIPANT_editor = 2; // waiting for add editor
var PROTOCOL_SET_PARTICIPANT_STATUS_name = 3; // waiting for status name
var PROTOCOL_SET_PARTICIPANT_STATUS_type = 4; // waiting for status type
var PROTOCOL_INCORRECT_SUBMISSION = 5; // waiting for participant name

// Protocol temporaries (used for multi-step protocol events)
var PROTOCOL_TEMP_name;

// GLOBAL APP VARIABLES:
var ws = false; // websocket (initially FALSE to imply it is not connected)
var display; // current Display object
var FPS = 30; // frames per second
var dT = Math.floor(1000/FPS); // delta time (between frames)

var protocolState = PROTOCOL_STANDBY;


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
        //console.log('WebSocket Error ' + error); TODO - what?
    };
    
    // If socket is closed, display notification alert, and set ws to false
    //  to indicate that it is no longer connected.
    ws.onclose = function(){
        notify("Disconnected from server.", NOTIFICATION_TYPE_ALERT);
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
    display = new DisplayChallengeMode();
    setTimeout(updateFrame, dT);
});


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
    /*
    - receive "ADD_PARTICIPANT"
        - receive participant name (unique)
        - receive participant editor
        ----- add that participant to the list -----
    - receive "SET_PARTICIPANT_STATUS"
        - receive participant name
        - receive: "STATUS_WORKING"
        - receive: "STATUS_FINISHED"
        - receive: "STATUS_FORFEIT"
        ----- adjust status accordinly -----
    - receive "INCORRECT_SUBMISSION"
        - receive participant name
        ----- announce the message -----
        
        PROTOCOL_STANDBY
var PROTOCOL_ADD_PARTICIPANT_name = 1; // adding participant, waiting for name
var PROTOCOL_ADD_PARTICIPANT_editor = 2; // adding participant, waiting for editor
var PROTOCOL_SET_PARTICIPANT_STATUS = 3; // waiting for status type
var PROTOCOL_INCORRECT_SUBMISSION = 4; // waiting for participant name
     */
     
    // if protocol is in standby mode, check for new instruction
    if(protocolState == PROTOCOL_STANDBY){
        if(data == "ADD_PARTICIPANT") // go to add participant mode
            protocolState = PROTOCOL_ADD_PARTICIPANT_name;
        
        else if(data == "SET_PARTICIPANT_STATUS") // go to set status mode
            protocolState = PROTOCOL_SET_PARTICIPANT_STATUS_name;
        
        else if(data == "INCORRECT_SUBMISSION") // go to wrong submission mode
            protocolState = PROTOCOL_INCORRECT_SUBMISSION;
    }
    
    // if protocol is in add participant mode and waiting for name:
    else if(protocolState == PROTOCOL_ADD_PARTICIPANT_name){
        PROTOCOL_TEMP_name = data;
        protocolState = PROTOCOL_ADD_PARTICIPANT_editor;
    }
    
    // if protocol is in add participant mode and waiting for editor:
    else if(protocolState == PROTOCOL_ADD_PARTICIPANT_editor){
        var newCompetitor = new ChallengeCompetitor(PROTOCOL_TEMP_name, data);
        display.addCompetitor(newCompetitor);
        protocolState = PROTOCOL_STANDBY;
    }
    
    // if protocol is in set status mode and waiting for name:
    else if(protocolState == PROTOCOL_SET_PARTICIPANT_STATUS_name){
        PROTOCOL_TEMP_name = data;
        protocolState = PROTOCOL_SET_PARTICIPANT_STATUS_type;
    }
    
    // if protocol is in set status mode and waiting for status type:
    else if(protocolState == PROTOCOL_SET_PARTICIPANT_STATUS_type){
        var competitor = display.getCompetitor(PROTOCOL_TEMP_name);
        if(competitor){
            switch(data){
                case "STATUS_WORKING":
                    competitor.status = PARTICIPANT_WORKING;
                    break;
                case "STATUS_FINISHED":
                    competitor.status = PARTICIPANT_FINISHED;
                    notify("" + PROTOCOL_TEMP_name + " finished!",
                        NOTIFICATION_TYPE_GOOD);
                    break;
                case "STATUS_FORFEIT":
                    competitor.status = PARTICIPANT_FORFEIT;
                    notify("" + PROTOCOL_TEMP_name + " gave up.",
                        NOTIFICATION_TYPE_BAD);
                    break;
                default:
                    break;
            }
        }
        protocolState = PROTOCOL_STANDBY;
    }
    
    else if(protocolState == PROTOCOL_INCORRECT_SUBMISSION){
        notify("" + data + " was incorrect.", NOTIFICATION_TYPE_ALERT);
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


// Queries Google Translate text-to-speech API to playback the given text.
//  NOTE: currently, this does not work on Firefox.    
function playText(text){
    if (text == "")
        return false;
    var audio = document.createElement("audio");
    audio.setAttribute("src",
        "http://translate.google.com/translate_tts?tl=en&q="
        + encodeURIComponent(text));
    audio.load();
    audio.play();
}
