
var xhrSuccessStatus = {
		// file protocol always yields status code 0, assume 200
		0: 200,
		// Support: IE9
		// #1450: sometimes IE returns 1223 when it should be 204
		1223: 204
	}

var ajaxBeforeSend = function(xhr, settings) {
         function getCookie(name) {
             var cookieValue = null;
             if (document.cookie && document.cookie != '') {
                 var cookies = document.cookie.split(';');
                 for (var i = 0; i < cookies.length; i++) {
                     var cookie = jQuery.trim(cookies[i]);
                     // Does this cookie string begin with the name we want?
                 if (cookie.substring(0, name.length + 1) == (name + '=')) {
                     cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                     break;
                 }
             }
         }
         return cookieValue;
         }
         if (!(/^http:.*/.test(settings.url) || /^https:.*/.test(settings.url))) {
             // Only send the token to relative URLs i.e. locally.
             xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
         }
    settings.converters["* streamed"]=true;
} ;

$.ajaxSetup({ 
    beforeSend: ajaxBeforeSend
});


// define transport ajax function for streaming data

var streamedTransport = function(streamCallback) {
    return $.ajaxTransport("streamed", function( options, originalOptions, jqXHR ) {
	return {
	    send: function( headers, completeCallback ) {
		var i,
		    xhr = options.xhr();
		
		xhr.open(
		    options.type,
		    options.url,
		    options.async,
		    options.username,
		    options.password
		);

		// Apply custom fields if provided
		if ( options.xhrFields ) {
		    for ( i in options.xhrFields ) {
			xhr[ i ] = options.xhrFields[ i ];
		    }
		}

		// Override mime type if needed
		if ( options.mimeType && xhr.overrideMimeType ) {
		    xhr.overrideMimeType( options.mimeType );
		}

		// X-Requested-With header
		// For cross-domain requests, seeing as conditions for a preflight are
		// akin to a jigsaw puzzle, we simply never set it to be sure.
		// (it can always be set on a per-request basis or even using ajaxSetup)
		// For same-domain requests, won't change header if already provided.
		if ( !options.crossDomain && !headers["X-Requested-With"] ) {
		    headers["X-Requested-With"] = "XMLHttpRequest";
		}
		
		// Set headers
		for ( i in headers ) {
		    xhr.setRequestHeader( i, headers[ i ] );
		}

		// Callback
		callback = function( type ) {
		    return function() {
			if ( type === "state" ) {
			    streamCallback(xhr.responseText)
			}
			
			else if ( callback ) {
			    callback = xhr.onload = xhr.onerror = null;
			    //console.log(xhr.responseText)
			    if ( type === "abort" ) {
				xhr.abort();
			    }
			    else if ( type === "error" ) {
				completeCallback(
				    // file: protocol always yields status 0; see #8605, #14207
				    xhr.status,
				    xhr.statusText
				);
			    } else {
				completeCallback(
				    xhrSuccessStatus[ xhr.status ] || xhr.status,
				    xhr.statusText,
				    // Support: IE9
				    // Accessing binary-data responseText throws an exception
				    // (#11426)
				    typeof xhr.responseText === "string" ? {
					text: xhr.responseText
				    } : undefined,
				    xhr.getAllResponseHeaders()
				);
			    }
			}
		    }
		};

		// Listen to events
		xhr.onload = callback();
		xhr.onreadystatechange = callback("state");
		xhr.onerror = callback("error");
		
		// Create the abort callback
		callback = callback("abort");
		
		try {
		    // Do send the request (this may raise an exception)
		    xhr.send( options.hasContent && options.data || null );
		} catch ( e ) {
		    // #14683: Only rethrow if this hasn't been notified as an error yet
		    if ( callback ) {
			throw e;
		    }
		}
	    },
	    
	    abort: function() {
		if ( callback ) {
		    callback();
		}
	    }
	}
    });
}



