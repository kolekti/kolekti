
    var topic_templates = ['default.xht'];

    var create_topic = function(folder, update_function) {
	var filename = $('#new_name').val();
	$.post('/topics/create/',
	       {
		   'model': $('.label-tpl').data('tpl'),
		   'topicpath': folder + "/" + filename
	       })
	    .success(
		update_function()
	    )
    };
    
		  
    var create_builder = function(e) {
	e.prepend(   
	    ['Nouveau module : ',
	     $('<input>',{ 'type':"text",
			   'id':'new_name',
			   'class':"form-control filename"
			 }),
	     'Modèle : ',
	     $('<span>',{ 'class':'btn-group',
			  'html':[$('<button>',{
			      'type':'button',
			      'class':'btn btn-default form-control',
			      'data-toggle':'dropdown',
			      'role':'button',
			      'aria-expanded':'false',
			      'html':[$('<span>',{
				  'class':'label-tpl',
				  'data-tpl':topic_templates[0],
				  'html':topic_templates[0]}),
				      ' ',
				      $('<span>',{
					  'class':'caret'})
				     ]}),
				  $('<ul>',{
				      'class':'dropdown-menu',
				      'role':'menu',
				      "id":"tpllist"
				  })]
			}
	      ),
	     $('<br>')
	    ]);

	$.each(topic_templates, function(i,v) {
	    $('<li>',{
		'class':'presentation',
		'html':$("<a>",{
		    'href':"#",
		    'class':'tpl-item',
		    'data-tpl':v,
		    'html':v
		})
	    }).appendTo('#tpllist');
	});
    }
    

$(document).ready(function() {
    $.get('/topics/templates/?lang='+kolekti.lang)
	.success(function(data) {
	    topic_templates = data;
	});
})