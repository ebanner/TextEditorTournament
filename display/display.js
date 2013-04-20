// Global Constants
var PARTICIPANT_WORKING = 0;
var PARTICIPANT_FINISHED = 1;
var PARTICIPANT_FORFEIT = 2;

var TEXT_BUBBLE_DURATION = 10; // seconds
var TEXT_BUBBLE_FADE_TIME = 1; // seconds

var DISPLAY_TEXT_COLOR = 0; // TODO - currently unused
var DISPLAY_DIVIDER_COLOR = 0; // TODO - currently unused
var DISPLAY_BACKGROUND_IMAGE = "images/bg.jpg";
var DISPLAY_WORKING_ICON = "images/what.png";
var DISPLAY_FINISHED_ICON = "images/victory.png";
var DISPLAY_FORFEIT_ICON = "images/cry.png";


// Display object that renders to the canvas, responsible for displaying the
//  screen as
function DisplayChallengeMode(){

    // canvas and context
    this.canvas = document.getElementById("screen");
    this.ctx = this.canvas.getContext("2d");
    
    // challenge information
    this.challengeNumber = 0;
    this.challengeName = "Challenge Name Here";
    
    // background image
    this.backgroundImage = new Image();
    this.backgroundImage.src = DISPLAY_BACKGROUND_IMAGE;
    
    // challenge status icons
    this.workingIcon = new Image();
    this.workingIcon.src = DISPLAY_WORKING_ICON;
    this.finishedIcon = new Image();
    this.finishedIcon.src = DISPLAY_FINISHED_ICON;
    this.forfeitIcon = new Image();
    this.forfeitIcon.src = DISPLAY_FORFEIT_ICON;
    
    // list of message bubbles on the screen
    this.textBubbles = new Array();
    
    // list of competitors displayed
    this.competitors = new Array();
    
    // TODO - temporary
    for(var i=0; i<15; i++){
        var c = new ChallengeCompetitor("name", "editor");
        c.status = i%3;
        this.competitors.push(c);
    }
    
    
    // Makes the canvas go into fullscreen mode. TODO- doesn't work.
    this.goFullScreen = function(){
        this.canvas.width = 1600;
        this.canvas.height = 1000;
        
        if(this.canvas.requestFullScreen)
            this.canvas.requestFullScreen();
        else if(this.canvas.webkitRequestFullScreen)
            this.canvas.webkitRequestFullScreen();
        else if(this.canvas.mozRequestFullScreen)
            this.canvas.mozRequestFullScreen();
    }
    
    
    // Add a message bubble to appear on the screen (drawn individually from
    //  the list until they expire). If the list already contains 10 bubbles,
    //  then that's too much to fit on the screen, so removes the oldest one.
    this.addMessage = function(text, colorStr){
        // if array already contains 10 bubbles, remove the oldest one (first)
        if(this.textBubbles.length >= 10)
            this.textBubbles.splice(0, 1);
        
        // add the new text bubble
        var bubble = new TextBubble(text, colorStr);
        this.textBubbles.push(bubble);
    }
    
    
    // Updates the canvas to draw every frame, after clearing it off.
    this.update = function(){
        // Clear off the screen.
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
        
        // Establish text sizes before going into drawing.
        var bigTextSize = Math.floor(this.canvas.width / 36);
        var midTextSize = Math.floor(this.canvas.width / 55);
        var smallTextSize = Math.floor(this.canvas.width / 80);
        
        // Establish general positions before going into drawing.
        var edgeTop = Math.floor(this.canvas.height / 11);
        var secondTop = Math.floor(this.canvas.height / 6);
        var edgeLeft = Math.floor(this.canvas.width / 40);
        var midpointX = Math.floor(this.canvas.width / 2.5);
        var rightWidth = this.canvas.width - midpointX;
        var lineWidth = Math.ceil(this.canvas.width / 270);
        
        
        // Draw background texture for left side.
        this.ctx.drawImage(this.backgroundImage,
            0, 0, this.canvas.width, this.canvas.height);
            
		
		// Draw the participant list (if at least one).
		var numCompetitors = this.competitors.length;
		if(numCompetitors >= 1){
		    // Compute box height: at least 1/15th of the canvas height.
		    var boxHeight = Math.floor(this.canvas.height / (numCompetitors+1));
		    boxHeight = Math.min(boxHeight, this.canvas.height/15);
		    
		    // Compute element positions.
		    var curY = 0;
		    var firstDivider = midpointX + Math.floor(rightWidth / 6.5);
		    var secondDivider = midpointX + Math.floor(rightWidth / 1.75);
		    var boxTextSize = Math.ceil(boxHeight/2.6);
		    var relativeTextY = Math.ceil((boxHeight/2) + (boxTextSize/3));
		    var textOffset = Math.ceil(rightWidth/60);
		    var firstTextX = midpointX + textOffset;
		    var secondTextX = firstDivider + textOffset;
		    var thirdTextX = secondDivider + textOffset;
		    var statusImageOffset = Math.floor(boxHeight / 8);
		    var statusImageSize = Math.floor(3 * (boxHeight / 4));
		    var statusImageX = 
		        Math.floor(((midpointX + firstDivider) / 2) - (statusImageSize / 2));
		    this.ctx.lineWidth = Math.ceil(lineWidth / 2);
		    
		    // First box is the title.
		    this.ctx.fillStyle = "#FFFFFF";
		    this.ctx.fillRect(midpointX, curY, rightWidth, boxHeight);
		    this.ctx.beginPath();
		        this.ctx.moveTo(midpointX, curY + boxHeight);
		        this.ctx.lineTo(this.canvas.width, curY + boxHeight);
		        this.ctx.stroke();
		    this.ctx.closePath();
		    this.ctx.fillStyle = "#000000";
		    this.ctx.font = "bold " + boxTextSize + "pt Arial";
		    this.ctx.fillText("Status", firstTextX, relativeTextY);
		    this.ctx.fillText("Participant", secondTextX, relativeTextY);
		    this.ctx.fillText("Editor", thirdTextX, relativeTextY);
		    
		    // Set for other sections.
		    this.ctx.font = "" + boxTextSize + "pt Arial";
		    curY += boxHeight;
		    
		    for(var i=0; i<numCompetitors; i++){
		    
		        // Draw rectangle to contain the color of the status.
		        var bgColor = "#FFFFFF";
		        var statusImage = this.workingIcon; // default working icon
		        switch(this.competitors[i].status){
		            case PARTICIPANT_WORKING:
		                bgColor = "#CCCCCC";
		                break;
		            case PARTICIPANT_FINISHED:
		                bgColor = "#AAFFAA";
		                statusImage = this.finishedIcon; // swap to finished icon
		                break;
		            case PARTICIPANT_FORFEIT:
		                bgColor = "#FF8888";
		                statusImage = this.forfeitIcon; // swap to forfeit icon
		                break;
		            default:
		                break;
		        }
		        this.ctx.fillStyle = bgColor;
		        this.ctx.fillRect(midpointX, curY, rightWidth, boxHeight);
		    
		        // Draw main box divider.
		        this.ctx.beginPath();
		            this.ctx.moveTo(midpointX, curY + boxHeight);
		            this.ctx.lineTo(this.canvas.width, curY + boxHeight);
		            this.ctx.stroke();
		        this.ctx.closePath();
		        
		        // Draw the status information.
		        this.ctx.drawImage(statusImage,
		            statusImageX, curY + statusImageOffset,
		            statusImageSize, statusImageSize);
		        this.ctx.fillStyle = "#000000";
		        this.ctx.fillText(this.competitors[i].participant,
		            secondTextX, relativeTextY + curY);
		        this.ctx.fillText(this.competitors[i].editor,
		            thirdTextX, relativeTextY + curY);
		        
		        // Incremement current y position for the next drawn box.
		        curY += boxHeight;
		    }
		    
		    // Draw first column divider (status|name).
		    this.ctx.beginPath();
		        this.ctx.moveTo(firstDivider, 0);
		        this.ctx.lineTo(firstDivider, curY);
		        this.ctx.stroke();
		    this.ctx.closePath();
		    
		    // Draw second column divider (name|editor).
		    this.ctx.beginPath();
		        this.ctx.moveTo(secondDivider, 0);
		        this.ctx.lineTo(secondDivider, curY);
		        this.ctx.stroke();
		    this.ctx.closePath();
		}
		
        
        // Draw the scaled title and challenge number.
		this.ctx.fillStyle = "#000000";
        this.ctx.font = "bold " + bigTextSize + "pt Arial";
		this.ctx.fillText("Challenge " + this.challengeNumber,
		    edgeLeft, edgeTop);
        this.ctx.font = "bold " + midTextSize + "pt Arial";
		this.ctx.fillText(this.challengeName, edgeLeft, secondTop);
		
		
		// Draw the text bubbles: first, calculate the position and size for
		//  the bubbles.
		var bubbleH = Math.ceil(this.canvas.height / 17);
		var bubbleW = midpointX - edgeLeft*2;
		var bubbleY = this.canvas.height - edgeLeft - bubbleH;
		var textX = edgeLeft + Math.floor(midpointX / 40);
		// Loop backwards - draw most recent bubbles first.
		for(var i=(this.textBubbles.length-1); i>=0; i--){
		    // update the bubble; if it is dead, remove it from the list
		    this.textBubbles[i].update();
		    if(this.textBubbles[i].isDead()){
		        this.textBubbles.splice(i, 1);
		        continue;
		    }
		    // draw the bubble if it isn't dead
		    this.textBubbles[i].draw(this.ctx,
		        edgeLeft, bubbleY, bubbleW, bubbleH, smallTextSize, textX);
		    bubbleY -= (bubbleH + Math.ceil(bubbleH / 4));
		}
		
		
		// Draw the MAIN DIVIDER (line separator).
		this.ctx.lineWidth = lineWidth;
		this.ctx.beginPath();
		    this.ctx.moveTo(midpointX, 0);
		    this.ctx.lineTo(midpointX, this.canvas.height);
		    this.ctx.stroke();
		this.ctx.closePath();
    }
}


// A self-updating TextBubble object that fades over time, and if it expired
//  (i.e. if its text is done lingering), flags itself as dead, which means
//  it should stop getting drawn (removed from list).
function TextBubble(text, colorStr){
    // The text that this bubble should display, and its color.
    this.text = text;
    this.color = colorStr;
    
    // Update timer values (translated to frames) to keep track of the
    //  transparency state and the lifespan of this text bubble.
    this.timeStep = 0;
    this.endTime = secondsToFrames(TEXT_BUBBLE_DURATION);
    var framesToFade = secondsToFrames(TEXT_BUBBLE_FADE_TIME);
    this.fadeTime = this.endTime - framesToFade;
    this.curAlpha = 1;
    this.alphaDelta = this.curAlpha / framesToFade;
    this.dead = false;
    
    // Updates the current time step to check if it's time to remove this
    //  bubble (flag itself as dead). Also, if it is time to start fading
    //  out the bubble, the current alpha will be calculated to reflect
    //  the state of the fadeout.
    this.update = function(){
        this.timeStep += 1;
        if(this.timeStep >= this.fadeTime){
            this.curAlpha -= this.alphaDelta;
        }
        if(this.timeStep >= this.endTime)
            this.dead = true;
    }
    
    // Draw this text bubble to the screen given the context, x and y position,
    //  box width and height, text size, and the X position of the text.
    // This draw function handles calulating the alpha values for the background
    //  and when the whole bubble is fading out.
    this.draw = function(ctx, x, y, w, h, textSize, textX){
        ctx.save();
            ctx.globalAlpha = this.curAlpha;
            ctx.fillStyle = "rgba(0, 0, 0, 0.5)";
            ctx.fillRect(x, y, w, h);
            ctx.fillStyle = this.color;
            ctx.font = "" + textSize + "pt Arial";
            ctx.fillText(this.text, textX, y + Math.floor(h/2 + textSize/3));
        ctx.restore();
    }
    
    // If this text bubble is dead, meaning it is time to remove it, then
    //  return TRUE. Otherwise, if it should still be drawn and updated,
    //  returns FALSE.
    this.isDead = function(){
        return this.dead;
    }
}


// A small struct containing the information about a specific participant
//  and their current challenge status.
function ChallengeCompetitor(participant, editor){
    // Participant meta info
    this.participant = participant;
    this.editor = editor;
    
    // Default status to working (challange in progress)
    this.status = PARTICIPANT_WORKING;
    
    // Time that a participant finished.
    this.finishedTime = 0;
}
