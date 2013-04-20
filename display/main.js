/* Contains the visual display data:
 *  Creates a websocket client that receives real-time updates from the server
 *  and displays them, along with audio playback.
 */


// GLOBAL CONSTANTS
var NOTIFICATION_TYPE_NORMAL = 0;
var NOTIFICATION_TYPE_SYS = 1;
var NOTIFICATION_TYPE_ALERT = 2;
var NOTIFICATION_TYPE_ERROR = 3;


// GLOBAL APP VARIABLES:
var ws = false; // websocket (initially FALSE to imply it is not connected)
var display; // current Display object
var dT = 1000/30; // delta time (between frames)


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
        ws.send("Hello, server!");
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
    
    // Set up inputBox to call sendMessage function.
    $("#inputBox").keyup(function(e){
        if(e.keyCode == 13) // enter
            //sendMessage(); TODO - change this back
            playText($("#inputBox").val());
    });
    
    // Start the canvas animator
    display = new DisplayChallengeMode();
    setTimeout(updateFrame, dT);
});


function goFullScreen(){
    display.goFullScreen();
}

// Called each frame (via Javascript events) to re-draw the entire canvas
//  and refresh it for the next frame.
function updateFrame(){
    display.update();
    setTimeout(updateFrame, dT);
}


// Parse a message received from the server through the websocket.
function parseServerMessage(data){
    alert(data); // TODO - just alerts for now
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
            colorStr = "#00FF00"; // green
            break;
        case NOTIFICATION_TYPE_ALERT:
            colorStr = "#FFFF00"; // yellow
            break;
        case NOTIFICATION_TYPE_ERROR:
            colorStr = "#FF0000"; // red
            break;
        case NOTIFICATION_TYPE_NORMAL:
        default:
            break; // white
    }
    display.addMessage(new TextBubble(colorStr));
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
