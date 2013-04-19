/* Contains the visual display data:
 *  Creates a websocket client that receives real-time updates from the server
 *  and displays them, along with audio playback.
 */

// When document is loaded, initialize the websocket, add a listener to the
//  input box, and zero-out all of the text values that may have been cached
//  from before.
$(document).ready(function(){
    // check if audio is supported in this browser
    var audioTagSupport = !!(document.createElement('audio').canPlayType);
    if (!audioTagSupport)
        alert("Can't play audio.");
        
    // TODO - init websockets here
    
    // set up inputBox to call sendMessage function
    $("#inputBox").keyup(function(e){
        if(e.keyCode == 13) // enter
            //sendMessage(); TODO - change this back
            playText($("#inputBox").val());
    });
    
    // clear all text fields/boxes
    $("#inputBox").val("");
    $("#textBox").val("");
});
    
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
