// Global values
var PARTICIPANT_WORKING = 0;
var PARTICIPANT_FINISHED = 1;
var PARTICIPANT_FORFEIT = 2;


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
    this.backgroundImage.src = "bg.jpg";
    
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
    //  the list until they expire).
    // TODO - if list is too big, remove the first.
    this.addMessage = function(text, colorStr){
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
        var smallTextSize = Math.floor(this.canvas.width / 75);
        
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
		    
		    // Compute line positions.
		    var curY = 0;
		    var firstDivider = midpointX + Math.floor(rightWidth / 6.5);
		    var secondDivider = midpointX + Math.floor(rightWidth / 1.75);
		    var boxTextSize = Math.ceil(boxHeight/2.6);
		    var relativeTextY = Math.ceil((boxHeight/2) + (boxTextSize/3));
		    var textOffset = Math.ceil(rightWidth/60);
		    var firstTextX = midpointX + textOffset;
		    var secondTextX = firstDivider + textOffset;
		    var thirdTextX = secondDivider + textOffset;
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
		        switch(this.competitors[i].status){
		            case PARTICIPANT_WORKING:
		                bgColor = "#CCCCCC";
		                break;
		            case PARTICIPANT_FINISHED:
		                bgColor = "#AAFFAA";
		                break;
		            case PARTICIPANT_FORFEIT:
		                bgColor = "#FF8888";
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
		        // TODO - draw status image here
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
		// Loop backwards - draw most recent bubbles first.
		for(var i=(this.textBubbles.length-1); i>=0; i--){
		    this.textBubbles[i].update();
		    this.textBubbles[i].draw(this.ctx,
		        edgeLeft, bubbleY, bubbleW, bubbleH, smallTextSize);
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
    //
    this.text = text;
    this.color = colorStr;
    
    this.update = function(){
        
    }
    
    this.draw = function(ctx, x, y, w, h, textSize){
        ctx.fillStyle = "rgba(0, 0, 0, 0.5)";
        ctx.fillRect(x, y, w, h);
        ctx.fillStyle = this.color;
        ctx.font = "" + textSize + "pt Arial";
        // TODO - fix
        ctx.fillText(this.text, x+5, y + Math.floor(h/2 + textSize/3));
    }
    
    this.isDead = function(){
        return false;
    }
}

function ChallengeCompetitor(participant, editor){
    // Participant meta info
    this.participant = participant;
    this.editor = editor;
    
    // Default status to working (challange in progress)
    this.status = PARTICIPANT_WORKING;
    
    this.finishedTime = 0;
}
