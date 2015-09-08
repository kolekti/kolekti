$(document).ready(function() {
    var widgets=[];					    
    var widget = function(wdef) {
	var w = $('<div>', {
	    "class":"panel panel-primary",
	    "html":[
		$('<div>', {
		    "class":"panel-heading",
		    "html":wdef.title
		}),
		$('<div>', {
		    "class":"panel-body",
		    "html":wdef.content()
		})
	    ]
	})
	$('#widgets').append(w);
	return w
    }


    var widgets_definitions = {
	'publications':{'title':'Dernières publications',
			'content':function() {
			    var wdiv =
			    $('<div>', {
				"class":"", //col-xs-12 col-sm-6 col-md-4",
				"html":
				$('<ul>', {
				    "class":"list-group",
				})
			    })
			    $.getJSON('/publications/list.json', function(data) {
				$.each(data.publications, function( i, pub ) {
				    console.log(pub);
				    wdiv.find('.list-group').append($('<li>', {
					"class":"list-group-item",
					"html":[
					    $('<h4>',{'html':pub.path}),
					    $('<p>',{html:formatTime(pub.time)}),
					    $('<div>',{
						html:
						$.map(pub.content, function(ev, iev) {
						    if (ev.event == "error")
							return $('<div>', {
							    "class" : "panel panel-alert",
								  "html": ev.msg
							});
						    if (ev.event == "lang") 
							return $('<hr>',{'html':$('<h4>', {
							    "html":$('<em>',{
								"html":ev.label
							    })
							})});
						    if (ev.event == "toc") 
							return $('<p>', {"html": "Trame : " + ev.file});
						    if (ev.event == "job") 
							return $('<p>', {"html": "Parametres : " + ev.label});
						    if (ev.event == "profile")
							return $('<h6>', {"html": ev.label});
				    		    if (ev.event == "result") 
							return $('<ul>', {
							    "html":$.map(ev.docs, function(doc) {
								return $('<li>', {
								    'html': [$('<span>', {'html':doc.type}),
									     $('<a>', {
										 'href': doc.url,
										 'target':"_blank",
										 'html': doc.label
									     })
									    ]
								})
							    })
							})
						})
					    })
					]
				    }));
				})
			    })
			    return wdiv;
			}
		       }
    }
	    
    if (localStorage) {
	var widgets_names, widgets_stored = localStorage.getItem("widgets")
	if (widgets_stored)
	    widgets_names = widgets_stored.split(',')
	else
	    widgets_names = ["publications"];
	$.each(widgets_names, function(i,wn) {
	    widgets.push(widget(widgets_definitions[wn]))
	});
	localStorage.setItem("widgets", widgets_names.join(','))
    }
})



	    
