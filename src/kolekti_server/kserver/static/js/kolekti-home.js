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
			    $('<div>', {
				"class":"col-sm",
				"html":
				$('<ul>', {
				    "class":"list-group",
				    "html":
				    $.getJSON('/publications/list.json', function(data) {
					$.each(data.publications, function( i, pub ) {
					    console.log(pub);
					    $('<li>', {
						"class":"list-group-item",
						"html":$.each(pub, function(iev, ev) {
						    if (ev.type == "error")
						});
					    });
					});
				    })
				})
			    })
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



	    
