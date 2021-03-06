// Global Constants
var PARTICIPANT_WORKING = 0;
var PARTICIPANT_FINISHED = 1;
var PARTICIPANT_FORFEIT = 2;

var TEXT_BUBBLE_DURATION = 8; // seconds
var TEXT_BUBBLE_FADE_TIME = 1; // seconds

var DISPLAY_FG_COLOR = "#000000";
var DISPLAY_BACKGROUND_IMAGE = "images/bg.png";
var DISPLAY_WORKING_ICON = "images/what.png";
var DISPLAY_FINISHED_ICON = "images/victory.png";
var DISPLAY_FORFEIT_ICON = "images/cry.png";


// Prototyle display: contains the standard variables used by all of the
//  display objects to follow.
function Display(){
    // canvas and context
    this.canvas = document.getElementById("screen");
    this.ctx = this.canvas.getContext("2d");
    
    // list of message bubbles on the screen
    this.textBubbles = new Array();
    
    // background image
    this.backgroundImage = new Image();
    this.backgroundImage.src = DISPLAY_BACKGROUND_IMAGE;
    
    
    // Makes the canvas go into fullscreen mode, and increases the resolution
    //  to a better quality.
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
    
    
    // Clears off the screen, and draws the background image.
    this.drawBG = function(){
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
        this.ctx.drawImage(this.backgroundImage, 0, 0,
            this.canvas.width, this.canvas.height);
    }
    
    
    // Timer values and event function that gets run whenever a timer ticks
    //  down. Override to use for custom timer events.
    this.endTime = -1; // time value when onTime event is triggered
    this.curTime = 0; // current display time
    this.onTime = function(){} // OVERRIDE this event function
    this.setEndTime = function(ticks){
        this.endTime = this.curTime + ticks;
    }
    
    // Standardly used variables that get updated each frame, and can be
    //  manually updated by themselves.
    this.midpointX = 0;
    this.edgeLeft = 0;
    this.smallTextSize = 0;
    
    // Update function for the standard values and time tick by 1. If current
    //  time matches endTime, runs the onTime function.
    this.updateStandardValues = function(){
        this.curTime++;
        if(this.curTime == this.endTime)
            this.onTime();
        
        this.midpointX = Math.floor(this.canvas.width / 2.5);
        this.edgeLeft = Math.floor(this.canvas.width / 25);
        this.smallTextSize = Math.floor(this.canvas.width / 80);
    }
    
    
    // Draws the message bubbles on the screen.
    this.drawMessageBubbles = function(){
        this.ctx.textAlign = "left";
        var bubbleH = Math.ceil(this.canvas.height / 17);
		var bubbleW = this.midpointX - Math.ceil(this.midpointX / 6.5);
		var bubbleY = this.canvas.height - this.edgeLeft - bubbleH;
		var textX = this.edgeLeft + Math.floor(this.midpointX / 40);
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
		        this.edgeLeft, bubbleY, bubbleW, bubbleH,
		        this.smallTextSize, textX);
		    bubbleY -= (bubbleH + Math.ceil(bubbleH / 4));
		}
    }
    
    
    // Updates and draws every frame.
    this.update = function(){
        // Override to add more functionality.
        this.drawBG();
        this.updateStandardValues();
        this.drawMessageBubbles();
    }
}


// The very first start-up display mode: just shows a welcome message.
function DisplayWelcomeMode(){

    // Updates the welcome screen every frame.
    this.update = function(){
        // Do standard per-frame updates:
        this.drawBG();
        this.updateStandardValues();
        this.drawMessageBubbles();
        
        this.ctx.textAlign = "center";
        this.ctx.fillStyle = DISPLAY_FG_COLOR;
		this.ctx.font = "bold " + Math.ceil(this.canvas.width/40) + "pt Calibri";
		this.ctx.fillText("Welcome to Text Editor Tournament 2013!",
		    Math.floor(this.canvas.width / 2),
		    Math.floor(this.canvas.height / 2))
    }
}
DisplayWelcomeMode.prototype = new Display();


// The very first start-up display mode: just shows a welcome message.
function DisplayInitMode(challengeId, challengeName, descriptionLines){
    
    // challenge information
    this.challengeId = challengeId;
    this.challengeName = challengeName;
    this.descriptionLines = descriptionLines;
    this.acceptingParticipants = new Array();
    
    // Parameter: string
    this.addAcceptingParticipant = function(participant){
        if(participant.length >= 16){
            participant = participant.substring(0, 16);
            participant += "...";
        }
        this.acceptingParticipants.push(participant);
    }


    // Updates the welcome screen every frame.
    this.update = function(){
        // Do standard per-frame updates:
        this.drawBG();
        this.updateStandardValues();
        this.drawMessageBubbles();
        
        // Establish text sizes before going into drawing.
        var bigTextSize = Math.floor(this.canvas.width / 36);
        var midTextSize = Math.floor(this.canvas.width / 55);
        var smallTextSize = Math.floor(this.canvas.width / 110);
        var descriptionTextSize = Math.floor(this.canvas.width / 60);
        
        // Establish general positions before going into drawing.
        var edgeTop = Math.floor(this.canvas.height / 10);
        var secondTop = Math.floor(this.canvas.height / 5.5);
        var descriptionTop = Math.floor(this.canvas.height / 2);
        var descriptionLineHeight = Math.floor(this.canvas.height / 17);
        var edgeLeft = Math.floor(this.canvas.width / 16);
        
        // display the challenge ID and name (title) here:
        this.ctx.fillStyle = DISPLAY_FG_COLOR;
        this.ctx.textAlign = "left";
        this.ctx.font =  "bold " + bigTextSize + "pt Calibri";
        this.ctx.fillText("Challenge " + this.challengeId,
            edgeLeft, edgeTop);
        this.ctx.font =  "bold " + midTextSize + "pt Calibri";
        this.ctx.fillText("Challenge " + this.challengeName,
            edgeLeft, secondTop);
        
        // draw each line of the description here:
        this.ctx.textAlign = "center";
        this.ctx.font =  "" + descriptionTextSize + "pt Calibri";
        var descriptionX = Math.floor(this.canvas.width/2);
        for(var i=0; i<this.descriptionLines.length; i++){
            this.ctx.fillText(this.descriptionLines[i],
                descriptionX, descriptionTop);
            descriptionTop += descriptionLineHeight;
        }
        
        // draw a box for each accepting participant here
        var boxSize = Math.ceil(this.canvas.width / 23);
        var boxDiff = boxSize + Math.ceil(boxSize / 4);
        var halfBoxSize = Math.floor(boxSize / 2);
        var boxY = Math.floor(this.canvas.height / 3.4);
        var boxX = Math.floor(
            (this.canvas.width / 2) -
            (boxDiff * (this.acceptingParticipants.length - 1)) / 2);
        var boxTextTop = boxY - halfBoxSize / 2;
        var boxTextBottom = boxY + boxSize + halfBoxSize / 1.1;
        this.ctx.font = "" + smallTextSize + "pt Arial";
        for(var i=0; i<this.acceptingParticipants.length; i++){
            this.ctx.fillStyle = "#33BB55";
            this.ctx.fillRect(boxX - halfBoxSize, boxY, boxSize, boxSize);
            var boxTextY = boxTextTop;
            if(i%2 != 0)
                boxTextY = boxTextBottom;
            this.ctx.fillStyle = DISPLAY_FG_COLOR;
            this.ctx.fillText(this.acceptingParticipants[i],
                boxX, boxTextY);
            boxX += boxDiff;
        }
    }
}
DisplayInitMode.prototype = new Display();


// Challenge Mode Display: responsible for drawing the canvas showing the
//  current challenge number and name, and messages that pop up, and
//  showing the current progress status of each participant doing the challenge.
function DisplayChallengeMode(challengeId, challengeName){
    
    // challenge information
    this.challengeNumber = challengeId;
    this.challengeName = challengeName;
    
    // challenge status icons
    this.workingIcon = new Image();
    this.workingIcon.src = DISPLAY_WORKING_ICON;
    this.finishedIcon = new Image();
    this.finishedIcon.src = DISPLAY_FINISHED_ICON;
    this.forfeitIcon = new Image();
    this.forfeitIcon.src = DISPLAY_FORFEIT_ICON;
    
    // list of competitors displayed
    this.competitors = new Array();
    
    // Adds a participant to the list of active competitors.
    this.addCompetitor = function(participant, editor){
        var newCompetitor = new ChallengeCompetitor(participant, editor);
        this.competitors.push(newCompetitor);
    }
    
    // Returns a competitor (if found) by the given participant name,
    //  followed by the index of the array said competitor is in.
    this.getCompetitor = function(competitorName){
        for(var i=0; i<this.competitors.length; i++){
            if(this.competitors[i].participant == competitorName)
                return [this.competitors[i], i];
        }
        return false;
    }
    
    
    // Randomly announce a dis to slow competitors each 12 seconds
    this.setEndTime(secondsToFrames(INSULT_DELAY_INITIAL));
    this.onTime = function() {
        var numStillWaiting = this.competitors.length - numFinished;
        if(numStillWaiting <= 0)
            return;
        var offset = Math.floor(Math.random() * numStillWaiting);
        var index = this.competitors.length - 1 - offset;
        announceLongWait(this.competitors[index].participant);
        this.setEndTime(secondsToFrames(INSULT_DELAY));
    }
    
    
    // Updates the canvas to draw every frame, after clearing it off.
    this.update = function(){
        // Do standard per-frame updates:
        this.drawBG();
        this.updateStandardValues();
        this.drawMessageBubbles();
		    
		// general line color
		this.ctx.strokeStyle = "#000000";
        
        // Establish text sizes before going into drawing.
        var bigTextSize = Math.floor(this.canvas.width / 36);
        var midTextSize = Math.floor(this.canvas.width / 55);
        var smallTextSize = Math.floor(this.canvas.width / 80);
        
        // Establish general positions before going into drawing.
        var edgeTop = Math.floor(this.canvas.height / 11);
        var secondTop = Math.floor(this.canvas.height / 6);
        //var edgeLeft = Math.floor(this.canvas.width / 40);
        var edgeLeft = Math.floor(this.canvas.width / 25);
        var midpointX = Math.floor(this.canvas.width / 2.5);
        var rightWidth = this.canvas.width - midpointX;
        var lineWidth = Math.ceil(this.canvas.width / 270);
        
        // left-align text
        this.ctx.textAlign = "left";
            
		
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
		    var firstTextXmid =
		        midpointX + Math.floor((firstDivider - midpointX) / 2);
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
		        this.ctx.fillStyle = "#000000";
		        this.ctx.textAlign = "center";
		        if(this.competitors[i].finishedPlace > 0){
		            this.ctx.fillText("" + this.competitors[i].finishedPlace,
		                firstTextXmid, relativeTextY + curY);
		        }
		        else{
    		        this.ctx.drawImage(statusImage,
		                statusImageX, curY + statusImageOffset,
		                statusImageSize, statusImageSize);
		        }
		        this.ctx.textAlign = "left";
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
		this.ctx.fillStyle = DISPLAY_FG_COLOR;
        this.ctx.font = "bold " + bigTextSize + "pt Arial";
		this.ctx.fillText("Challenge " + this.challengeNumber,
		    edgeLeft, edgeTop);
        this.ctx.font = "bold " + midTextSize + "pt Arial";
		this.ctx.fillText(this.challengeName, edgeLeft, secondTop);
		
		
		// Draw the MAIN DIVIDER (line separator).
		this.ctx.strokeStyle = "#00FF00";
		this.ctx.lineWidth = lineWidth;
		this.ctx.beginPath();
		    this.ctx.moveTo(midpointX, 0);
		    this.ctx.lineTo(midpointX, this.canvas.height);
		    this.ctx.stroke();
		this.ctx.closePath();
    }
}
DisplayChallengeMode.prototype = new Display();


// Display mode for showing after-challenge data, including info about the
//  last challenge, as well as general editor stats (i.e. which editor
//  is currently in the lead).
function DisplayStatsMode(){
    
    this.averageTime = "";
    this.editorTimes = new Array();
    this.participantTimes = new Array();
    
    this.addEditorTime = function(editor, time){
        this.editorTimes.push([editor, time]);
    }
    this.addParticipantTime = function(participant, editor, time){
        this.participantTimes.push([participant, editor, time]);
    }
    this.setAverageTime = function(time){
        this.averageTime = time;
    }
    
    // called each frame to update
    this.curPulseAlpha = 0.5;
    this.curBlueVal = 0;
    this.blueDelta = (200 / secondsToFrames(0.5));
    this.pulseDelta = (0.5 / secondsToFrames(0.25));
    this.update = function(){
        // Do standard per-frame updates:
        this.drawBG();
        this.updateStandardValues();
        this.drawMessageBubbles();
        
        // update alpha for pulsing winner
        this.curPulseAlpha += this.pulseDelta;
        this.curBlueVal += this.blueDelta;
        if(this.curBlueVal <= 0 || this.curBlueVal >= 200)
            this.blueDelta *= -1;
        if(this.curPulseAlpha <= 0.25 || this.curPulseAlpha >= 1){
            this.pulseDelta *= -1;
        }
        
        // calculate re-used values
        var centerX = Math.floor(this.canvas.width / 2);
        var topY = Math.floor(this.canvas.height / 8);
        var bigFont = "bold " + Math.ceil(this.canvas.width/35) + "pt Calibri";
        var normalFont = "" + Math.ceil(this.canvas.width/65) + "pt Calibri";
        var columnTitleFont = "bold "
            + Math.ceil(this.canvas.width/60) + "pt Calibri";
        var leftCenterX = Math.floor((centerX/2) - (this.canvas.width/20));
        var rightCenterX = centerX + leftCenterX;
        var topOfColumns = Math.floor(topY * 1.7);
        var thinLineWidth = Math.ceil(this.canvas.width / 500);
        
        // set stroke and fill styles
        this.ctx.fillStyle = DISPLAY_FG_COLOR;
		this.ctx.strokeStyle = DISPLAY_FG_COLOR;
        
        // draw average time
        this.ctx.textAlign = "center";
		this.ctx.font = bigFont;
		this.ctx.fillText("Average Time: " + this.averageTime + " (ms)",
		    centerX, topY);
	    
	    // draw column headers
		var halfDivSize = Math.ceil(this.canvas.width / 12);
		var divHeight = Math.floor(this.canvas.height / 15);
		var curY = topOfColumns + divHeight;
		var distFromMid = Math.ceil(this.canvas.width / 40);
	    this.ctx.font = columnTitleFont;
	    this.ctx.textAlign = "right";
	    this.ctx.fillText("Editor", leftCenterX - distFromMid, curY);
	    this.ctx.textAlign = "left";
	    this.ctx.fillText("Time (ms)", leftCenterX + distFromMid, curY);
		
		// draw editors by time finished
		this.ctx.font = normalFont;
		for(var i=0; i<this.editorTimes.length; i++){
		    // if first place, highlight it in green!
		    if(i == 0){
		        this.ctx.save();
		            this.ctx.fillStyle = "#00FF00";
		            this.ctx.globalAlpha = this.curPulseAlpha;
		            this.ctx.fillRect(
		                leftCenterX - halfDivSize*2,
		                curY + Math.floor(divHeight/3),
		                halfDivSize*4, Math.floor(0.9 * divHeight));
		        this.ctx.restore();
		    }
		    // if last place, highlight it red!
		    else if(i == (this.editorTimes.length - 1)){
		        this.ctx.save();
		            this.ctx.fillStyle = "#FF0000";
		            this.ctx.globalAlpha = 0.25;
		            this.ctx.fillRect(
		                leftCenterX - halfDivSize*2,
		                curY + Math.floor(divHeight/3),
		                halfDivSize*4, Math.floor(0.9 * divHeight));
		        this.ctx.restore();
		    }
		    curY += divHeight;
		    this.ctx.textAlign = "right";
		    this.ctx.fillText(
		        this.editorTimes[i][0],
		        leftCenterX - distFromMid, curY);
		    this.ctx.textAlign = "left";
		    this.ctx.fillText(
		        this.editorTimes[i][1],
		        leftCenterX + distFromMid, curY);
		}
		
		// draw left side divider
		this.ctx.lineWidth = thinLineWidth;
        this.ctx.beginPath();
		    this.ctx.moveTo(leftCenterX, topOfColumns);
		    this.ctx.lineTo(leftCenterX, curY + divHeight);
		    this.ctx.stroke();
	    this.ctx.closePath();
		
		//  draw column headers
		curY = topOfColumns + divHeight;
	    this.ctx.font = columnTitleFont;
	    this.ctx.textAlign = "right";
	    this.ctx.fillText("Participant",
	        rightCenterX - distFromMid - halfDivSize, curY);
	    this.ctx.textAlign = "center";
	    this.ctx.fillText("Editor", rightCenterX, curY);
	    this.ctx.textAlign = "left";
	    this.ctx.fillText("Time (ms)",
	        rightCenterX + distFromMid + halfDivSize, curY);
		
		// draw participants by time finished
		this.ctx.font = normalFont;
		for(var i=0; i<this.participantTimes.length; i++){
		    // if first place, highlight it in green!
		    if(i == 0){
		        this.ctx.save();
		            this.ctx.fillStyle = "#00FF00";
		            this.ctx.globalAlpha = 0.25;
		            this.ctx.fillRect(
		                rightCenterX - halfDivSize*3,
		                curY + Math.floor(divHeight/3),
		                halfDivSize*6, Math.floor(0.9 * divHeight));
		        this.ctx.restore();
		    }
		    // if last place, highlight it red!
		    else if(i == (this.participantTimes.length - 1)){
		        this.ctx.save();
		            this.ctx.fillStyle = "#FF0000";
		            this.ctx.globalAlpha = 0.25;
		            this.ctx.fillRect(
		                rightCenterX - halfDivSize*3,
		                curY + Math.floor(divHeight/3),
		                halfDivSize*6, Math.floor(0.9 * divHeight));
		        this.ctx.restore();
		    }
		    curY += divHeight;
		    this.ctx.textAlign = "right";
		    this.ctx.fillText(
		        this.participantTimes[i][0],
		        rightCenterX - distFromMid - halfDivSize, curY);
		    this.ctx.textAlign = "center";
		    this.ctx.fillText(
		        this.participantTimes[i][1],
		        rightCenterX, curY);
		    this.ctx.textAlign = "left";
		    this.ctx.fillText(
		        this.participantTimes[i][2],
		        rightCenterX + distFromMid + halfDivSize, curY);
		}
		
		// draw rightside divider 1 (left)
		curY += divHeight;
        this.ctx.beginPath();
		    this.ctx.moveTo(rightCenterX - halfDivSize, topOfColumns);
		    this.ctx.lineTo(rightCenterX - halfDivSize, curY);
		    this.ctx.stroke();
	    this.ctx.closePath();
		
		// draw rightside divider 2 (right)
        this.ctx.beginPath();
		    this.ctx.moveTo(rightCenterX + halfDivSize, topOfColumns);
		    this.ctx.lineTo(rightCenterX + halfDivSize, curY);
		    this.ctx.stroke();
	    this.ctx.closePath();
    }
}
DisplayStatsMode.prototype = new Display();


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
		    ctx.fillStyle = "#505050";
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
    this.finishedPlace = 0;
}
