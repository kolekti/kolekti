
var topic_templates = ['default.xht'];

var create_topic = function(browser, folder, update_function, error_function) {
    var filename = $(browser).find('#new_name').val();
    var lang = folder.split('/')[2]
    var topic_folder = folder.split('/').splice(4). join('/')

	$.post(Urls.kolekti_topic_create(kolekti.project, lang, topic_folder + filename),
	       {
		   'model': $('.label-tpl').data('tpl')
	       })
	    .done(
		    function(topicpath) {
		        update_function()
		    })
        .fail(
		    function(data) {
                console.log('error')
                console.log(data)
                error_function(data.responseJSON.error)
		    })
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
	var url= Urls.kolekti_templates_json(kolekti.project, kolekti.lang)
    $.get(url)
	.success(function(data) {
	    topic_templates = data;
	});
})
