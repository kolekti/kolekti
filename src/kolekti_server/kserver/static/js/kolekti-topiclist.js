$(document).ready(function() {

    $('#btn_create').on("click", function(e) {
	var folder = $('.browserparent').data('path');
	var filename = $('#new_name').val()
	$.post('/topics/create/',
	       {
		   'model': $('.label-tpl').data('tpl'),
		   'topicpath': folder + "/" + filename
	       })
	    .success(
		window.location.reload()
	    )
    })
    

    kolekti_browser({'root':'/sources/'+kolekti.lang+'/topics',
		     'parent':".browserparent",
		     'buttonsparent':".buttons",
		     'mode':"selectonly",
		     'modal':"no",
		     'os_actions':'yes'
		    })
	.select(
	    function(path) {
		window.open('/topics/edit/?topic='+path);
	    }
	)
    $.get('/topics/templates/?lang='+kolekti.lang)
    .success(function(data) {
	$('<div>',{ 'class':'btn-group',
		    'html':[$('<button>',{
			'type':'button',
			'class':'btn btn-default',
			'data-toggle':'dropdown',
			'role':'button',
			'aria-expanded':'false',
			'html':[$('<span>',{
			    'class':'label-tpl',
			    'data-tpl':data[0],
			    'html':data[0]}),
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
	 ).appendTo("#tpl");
	$.each(data, function(i,v) {
	    $('<li>',{
		'class':'presentation',
		'html':$("<a>",{
		    'href':"#",
		    'class':'tpl-item',
		    'data-tpl':v,
		    'html':v
		})
	    }).appendTo('#tpllist');
	})
    })
    
    $('#tpl').on('click', '.tpl-item',function(e){
	e.preventDefault();
	$('.label_tpl').html($(this).data('tpl'))
	$('.label_tpl').data('tpl',$(this).data('tpl'));
    })
	

})
