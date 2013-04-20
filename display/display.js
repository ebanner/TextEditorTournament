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
    
    for(var i=0; i<15; i++){
        this.competitors.push(new ChallengeCompetitor("name", "editor"));
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
    
    
    // Updates the canvas to draw every frame, after clearing it off.
    this.update = function(){
        // clear off the screen
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
        
        // establish text sizes before going into drawing
        var bigTextSize = Math.floor(this.canvas.width / 36);
        var midTextSize = Math.floor(this.canvas.width / 55);
        
        // establish general positions before going into drawing
        var cornerTop = Math.floor(this.canvas.height / 11);
        var secondTop = Math.floor(this.canvas.height / 6);
        var cornerLeft = Math.floor(this.canvas.width / 40);
        var midpointX = Math.floor(this.canvas.width / 2.5);
        var rightWidth = this.canvas.width - midpointX;
        var lineWidth = Math.ceil(this.canvas.width / 270);
        
        // draw background texture for left side
        this.ctx.drawImage(this.backgroundImage,
            0, 0, this.canvas.width, this.canvas.height);
            
		
		// draw the participant list (if at least one)
		var numCompetitors = this.competitors.length;
		if(numCompetitors >= 1){
		    // compute box height: at least 1/15th of the canvas height
		    var boxHeight = Math.floor(this.canvas.height / (numCompetitors+1));
		    boxHeight = Math.min(boxHeight, this.canvas.height/15);
		    
		    // compute line positions
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
		    
		    // first box is the title
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
		    
		    // set for other sections
		    this.ctx.font = "regular " + boxTextSize + "pt Arial";
		    curY += boxHeight;
		    
		    for(var i=0; i<numCompetitors; i++){
		    
		        // draw rectangle to contain the color of the status
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
		    
		        // draw main box divider
		        this.ctx.beginPath();
		            this.ctx.moveTo(midpointX, curY + boxHeight);
		            this.ctx.lineTo(this.canvas.width, curY + boxHeight);
		            this.ctx.stroke();
		        this.ctx.closePath();
		        
		        // incremement current y position for the next drawn box.
		        curY += boxHeight;
		    }
		        
		    // draw first column divider (status|name)
		    this.ctx.beginPath();
		        this.ctx.moveTo(firstDivider, 0);
		        this.ctx.lineTo(firstDivider, curY);
		        this.ctx.stroke();
		    this.ctx.closePath();
		    
		    // draw second column divider (name|editor)
		    this.ctx.beginPath();
		        this.ctx.moveTo(secondDivider, 0);
		        this.ctx.lineTo(secondDivider, curY);
		        this.ctx.stroke();
		    this.ctx.closePath();
		}
		
        
        // draw the scaled title and challenge number
		this.ctx.fillStyle = "#000000";
        this.ctx.font = "bold " + bigTextSize + "pt Arial";
		this.ctx.fillText("Challenge " + this.challengeNumber,
		    cornerLeft, cornerTop);
        this.ctx.font = "bold " + midTextSize + "pt Arial";
		this.ctx.fillText(this.challengeName, cornerLeft, secondTop);
		
		// draw the line separator
		this.ctx.lineWidth = lineWidth;
		this.ctx.beginPath();
		    this.ctx.moveTo(midpointX, 0);
		    this.ctx.lineTo(midpointX, this.canvas.height);
		    this.ctx.stroke();
		this.ctx.closePath();
    }
}


function TextBubble(){
    //
}

function ChallengeCompetitor(participant, editor){
    // Participant meta info
    this.participant = participant;
    this.editor = editor;
    
    // Default status to working (challange in progress)
    this.status = PARTICIPANT_WORKING;
    
    this.finishedTime = 0;
}
