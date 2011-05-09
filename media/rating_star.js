// When the DOM is ready....

/*
 This function generates a form containing a row of images (each 25x25), which when deselected are
 emptyImage, and selected are fullImage. Under each image is an entry of optionNames, and the first 
 defaultValue of them are selected. When a user makes a selection (some number of the images), the 
 number of images the user selects is sent to "submit/" as Rating_Value, and ratingname is sent as 
 Rating_Name. This is asynchronous. 
 
 This is based upon the 5-star rating code, and expanded to be used for the Hours and Grade input 
 as well.
 */
function moonStars(ratingname, defaultValue, emptyImage, fullImage, optionNames)
{
	
	
	//Generate the actual form of images
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
	//generate the table of image labels
	for(count=1; count< optionNames.length+1; count=count+1)
	{
		document.write("<td width=\"25\" style=\" text-align: center; padding: 0; border: 0; margin: 0;\">")
		document.write(optionNames[count-1])
		document.write("</td>")
	}
	document.write("</tr></table>")
	
	//add the async function that colors and submits the image form
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
		   tip: '[VALUE] / '+optionNames.length, //Mouse rollover tip  
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

/*
 This is a shortcut to use moonStars to create a simple 5-star rating that submits under the name ratingname, 
 with some default value (between 1 and 5, or no default)
 */
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

/*
 Given the id of a form, and the id of its submit button, this function will submit the form asynchronously
 when the submit button is clicked. It will decrease the opacity (make visible) of the element with id loadingDivId when the 
 form is being submitted, and then hide it again when the form is done. Depending on whether the server responded
 or threw an error, the form will then decrease the opacity (make visible) the element with the id 
 successDivId or failDivId for 3 seconds
 */
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

/*
 Call this function instead of drawing a submit button on a form. It will use its own submit button (the blue rectangular image one)
 and rig the form to submit asyncronously using mooForm. While loading, a loading symbol will appear next to the submit button, followed
 by a check mark for success or an x for failure, which disappear after 3 seconds. 
 */
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

/*
 This function uses mooSubmit to build a 480 wide comment submission form. It titles the comment commentName, 
 fills the comment value with defaultValue, the privacy checkbox with defaultPrivacy. The form will have id 
 commentId, with the textarea input commentId+"_Text" and the privacy box commentId+"_Privacy." The form submits
 to "submit/" asynchronously. It requires the existence fo the CSS class Rating_item.
 */
function mooComment(commentId, commentName, defaultValue, defaultPrivacy)
{
	document.write("<form id=\""+commentId+"\" action=\"submit/\" method=\"POST\"  class=\"Rating_item\" >");
	document.write(commentName);
	document.write("<br />");
	document.write("<textarea   title=\"Write a comment...\" name=\""+commentId+"_Text\" style=\"height: 50px; width: 480px;\">");
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


function MM_findObj(n, d) { //v4.01
	var p,i,x;  if(!d) d=document; if((p=n.indexOf("?"))>0&&parent.frames.length) {
		d=parent.frames[n.substring(p+1)].document; n=n.substring(0,p);}
	if(!(x=d[n])&&d.all) x=d.all[n]; for (i=0;!x&&i<d.forms.length;i++) x=d.forms[i][n];
	for(i=0;!x&&d.layers&&i<d.layers.length;i++) x=MM_findObj(n,d.layers[i].document);
	if(!x && d.getElementById) x=d.getElementById(n); return x;
}

function MM_preloadImages() { //v3.0
	var d=document; if(d.images){ if(!d.MM_p) d.MM_p=new Array();
		var i,j=d.MM_p.length,a=MM_preloadImages.arguments; for(i=0; i<a.length; i++)
			if (a[i].indexOf("#")!=0){ d.MM_p[j]=new Image; d.MM_p[j++].src=a[i];}}
}

function MM_swapImgRestore() { //v3.0
	var i,x,a=document.MM_sr; for(i=0;a&&i<a.length&&(x=a[i])&&x.oSrc;i++) x.src=x.oSrc;
}

function MM_swapImage() { //v3.0
	var i,j=0,x,a=MM_swapImage.arguments; document.MM_sr=new Array; for(i=0;i<(a.length-2);i+=3)
		if ((x=MM_findObj(a[i]))!=null){document.MM_sr[j++]=x; if(!x.oSrc) x.oSrc=x.src; x.src=a[i+2];}
}

