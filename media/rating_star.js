// When the DOM is ready....
function moonStarStars(ratingname)
{
	
	
	
	document.write("<form name=\""+ratingname+"form\">");
	for(count=1; count<=5; count=count+1)
	{
		document.write("<input type=\"radio\" name=\""+ratingname+"buttons\" value=\""+count+"\" />");
	}
	document.write("</form>");
	
	
	window.addEvent("domready",function() {  
					
		MooStarRatingImages.defaultImageFolder = '/media/'; //Default images folder definition. You will use your own  

		// Create our instance  
		// Advanced options  
		var advancedRating = new MooStarRating({  
		   form: ratingname+'form', //Form name   
		   radios: ratingname+'buttons', //Radios name  
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
			 data: {Rating_Value: value, Rating_Name: ratingname}  
			 });  
		   requestHTMLData.send();  
		   }  
		   });          
					
	}); 
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