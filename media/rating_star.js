// When the DOM is ready....
function moonStars(ratingname, defaultValue, emptyImage, fullImage, optionNames)
{
	
	
	
	document.write("<form name=\""+ratingname+"form\" class=\"Rating_item\" >");
	for(count=1; count< optionNames.length+1; count=count+1)
	{
		document.write("<input type=\"radio\" name=\""+ratingname+"buttons\" value=\""+(count)+"\" ");
		if (defaultValue == count)
		{
			document.write("checked=\"True\"")
		}
		document.write("/>");
	}
	document.write("</form><table cellspacing=\"0\"  class=\"Rating_item\"><tr>");
	for(count=1; count< optionNames.length+1; count=count+1)
	{
		document.write("<td width=\"25\" style=\" text-align: center; padding: 0; border: 0; margin: 0;\">")
		document.write(optionNames[count-1])
		document.write("</td>")
	}
	document.write("</tr></table>")
	
	
	window.addEvent("domready",function() {  
					
		MooStarRatingImages.defaultImageFolder = '/media/'; //Default images folder definition. You will use your own  

		// Create our instance  
		// Advanced options  
		var advancedRating = new MooStarRating({  
		   form: ratingname+'form', //Form name   
		   radios: ratingname+'buttons', //Radios name  
		   half: false, //if you need half star rating just make this true  
		   imageEmpty: emptyImage, //Default images are in definition. You will use your own  
		   imageFull:  fullImage,  
		   imageHover: null,   
		   width: 25,
		   height: 25,   
		   tip: ' <i>[VALUE] / '+optionNames.length+'</i>', //Mouse rollover tip  
		   tipTarget: $('htmlTip'), //Tip element  
		   tipTargetType: 'html', //Tip type is HTML   
		   
		   // Send ajax request to server to save rating 
		   onClick: function(value) {  
		   
		   var requestHTMLData = new Request({  
			 url: 'submit/',  
			 data: {Rating_Value: value, Rating_Name: ratingname}  
			 });  
		   requestHTMLData.send();  
		   }  
		   });          
					
	}); 
}


function moonStarStars(ratingname, defaultValue)
{
	moonStars(ratingname, defaultValue, 'star_x_gray.png', 'star_x_gold.png', ["","","","",""])
}


// Hides the loading div, and shows the el div for
// a period of four seconds.
var showHide = function( el, effects ){
	effects.loading.set(0);
	(effects[ el ]).start(0,1);
	(function(){ (effects[ el ]).start(1,0); }).delay( 4000 );
}

function mooForm(formId, submitId, loadingDivId, successDivId, failDivId)
{
	var effects = {
		'loading': new Fx.Tween( loadingDivId, {property:'opacity', duration:200 } ),
		'success': new Fx.Tween( successDivId, {property:'opacity', duration:200 } ),
		'fail': new Fx.Tween( failDivId, {property:'opacity', duration:200 } )
	};
	
	
	$(formId).set('send', {url:'submit.php', method:'POST'});
	// Listen for click events on the submit button.
	$(submitId).addEvent( 'click', function(evt){
						 // Stops the submission of the form.
						 new Event(evt).stop();
						 
						 
						 ( new Request({ 
									   url: $(formId).action, 
									   data:document.id(formId), 
									   method: 'post', 
									   onRequest: function(){
									   // Show loading div.
									   effects.loading.start( 1,0 );
									   }.bind(this),
									   onSuccess: function(){
									   // Hide loading and show success for 3 seconds.
									   showHide( 'success', effects );
									   }.bind(this),
									   onFailure: function(){
									   // Hide loading and show fail for 3 seconds.
									   showHide( 'fail', effects );
									   }.bind(this)
									   }) 
						  ).send() 
						 } );
}

function mooSubmit(formId)
{
	document.write("<span>");
	document.write("<input type=\"image\" src=\"/media/submit_button.png\" height=\"25\" width=\"60\" id=\""+formId+"_submit\" value=\"submit\" />");
	document.write("<span id=\"response\" class=\"response\" style=\"position: relative; left: 5px; top: 0; padding: 5px; \">");
	document.write("<img width=\"16\" height=\"16\" src=\"/media/ajax-loader.gif\" id=\""+formId+"_loading\" class=\"loading\" style=\"position: relative; top: 0; left: 0; position:absolute; visibility:hidden; \"/>");
	document.write("<img width=\"16\" height=\"16\" src=\"/media/35px-Green_tick.svg.png\" id=\""+formId+"_success\" class=\"success\" style=\"position: absolute; top: 0; left: 0; position:absolute; visibility:hidden; \"/>");
	document.write("<img width=\"16\" height=\"16\" src=\"/media/35px-Red_x.svg.png\" id=\""+formId+"_failure\" class=\"failure\" style=\"position: absolute; top: 0; left: 0; position:absolute; visibility:hidden; \"/>");
	document.write("</span>");
	document.write("</span>");
	mooForm(formId, formId+"_submit", formId+"_loading", formId+"_success", formId+"_failure");
}


function mooComment(commentId, commentName, defaultValue, defaultPrivacy)
{
	document.write("<form id=\""+commentId+"\" action=\"submit/\" method=\"POST\"  class=\"Rating_item\" >");
	document.write(commentName);
	document.write("<br />");
	document.write("<textarea   title=\"Write a comment...\" name=\""+commentId+"_Text\" style=\"height: 50px; width: 750px;\">");
	document.write(defaultValue);
	document.write("</textarea>");
	document.write("<table><tr><td width=\"200\">");
	mooSubmit(commentId);
	document.write("</td><td>");
	document.write("<input type=\"checkbox\" name=\""+commentId+"_Privacy\" ");
	if (defaultPrivacy)
	{
		document.write("checked=\"True\"");
	}
	document.write("/>");
	document.write("Public Comment");
	document.write("</td></table></form><br />");
}


/*
 
 
 // When the DOM is ready....  
 window.addEvent("domready",function() {  
    
  MooStarRatingImages.defaultImageFolder = '/media/'; //Default images folder definition. You will use your own  
     
   // Create our instance  
   // Advanced options  
   var advancedRating = new MooStarRating({  
    form: 'Overall_Ratingsform', //Form name   
    radios: 'Overall_Rating', //Radios name  
    half: false, //if you need half star rating just make this true  
    imageEmpty: 'star_x_gray.png', //Default images are in definition. You will use your own  
    imageFull:  'star_x_gold.png',  
    imageHover: null,   
    width: 25,
    height: 25,   
    tip: 'Rate <i>[VALUE] / 5</i>', //Mouse rollover tip  
    tipTarget: $('htmlTip'), //Tip element  
    tipTargetType: 'html', //Tip type is HTML   
      
    // Send ajax request to server to save rating using "rating.php"  
    onClick: function(value) {  
            
     var requestHTMLData = new Request({  
     url: 'rating.php',  
     data: {Overall_Rating: value}  
     });  
     requestHTMLData.send();  
     }  
     });          
     
  });  
 //============================================================================= 
  window.addEvent("domready",function() {  
    
  MooStarRatingImages.defaultImageFolder = '/media/';
     var advancedRating = new MooStarRating({  
    form: 'Content_Ratingsform', //Form name   
    radios: 'Content_Rating', //Radios name  
    half: false, //if you need half star rating just make this true  
    imageEmpty: 'star_x_gray.png', //Default images are in definition. You will use your own  
    imageFull:  'star_x_gold.png',  
    imageHover: null,   
    width: 25,
    height: 25,   
    tip: 'Rate <i>[VALUE] / 5</i>', //Mouse rollover tip  
    tipTarget: $('htmlTip'), //Tip element  
    tipTargetType: 'html', //Tip type is HTML   
      
    // Send ajax request to server to save rating using "rating.php"  
    onClick: function(value) {  
            
     var requestHTMLData = new Request({  
     url: 'rating.php',  
     data: {Content_Rating: value}  
     });  
     requestHTMLData.send();  
     }  
     });          
     
  });  
 //=============================================================================
  window.addEvent("domready",function() {  
    
  MooStarRatingImages.defaultImageFolder = '/media/';
    var advancedRating = new MooStarRating({  
    form: 'Teaching_Ratingsform', //Form name   
    radios: 'Teaching_Rating', //Radios name  
    half: false, //if you need half star rating just make this true  
    imageEmpty: 'star_x_gray.png', //Default images are in definition. You will use your own  
    imageFull:  'star_x_gold.png',  
    imageHover: null,   
    width: 25,
    height: 25,   
    tip: 'Rate <i>[VALUE] / 5</i>', //Mouse rollover tip  
    tipTarget: $('htmlTip'), //Tip element  
    tipTargetType: 'html', //Tip type is HTML   
      
    // Send ajax request to server to save rating using "rating.php"  
    onClick: function(value) {  
            
     var requestHTMLData = new Request({  
     url: 'rating.php',  
     data: {Teaching_Rating: value}  
     });  
     requestHTMLData.send();  
     }  
     });          
     
  });      
  //============================================================================
  window.addEvent("domready",function() {  
    
  MooStarRatingImages.defaultImageFolder = '/media/';
     var advancedRating = new MooStarRating({  
    form: 'Grading_Ratingsform', //Form name   
    radios: 'Grading_Rating', //Radios name  
    half: false, //if you need half star rating just make this true  
    imageEmpty: 'star_x_gray.png', //Default images are in definition. You will use your own  
    imageFull:  'star_x_gold.png',  
    imageHover: null,   
    width: 25,
    height: 25,   
    tip: 'Rate <i>[VALUE] / 5</i>', //Mouse rollover tip  
    tipTarget: $('htmlTip'), //Tip element  
    tipTargetType: 'html', //Tip type is HTML   
      
    // Send ajax request to server to save rating using "rating.php"  
    onClick: function(value) {  
            
     var requestHTMLData = new Request({  
     url: 'rating.php',  
     data: {Grading_Rating: value}  
     });  
     requestHTMLData.send();  
     }  
     });          
     
  });       
*/