$(document).ready( function () {
    var enable_save = function() {
	$('#btn_save').removeClass('disabled');
	$('#btn_save').removeClass('btn-default');
	$('#btn_save').addClass('btn-warning');
    }

    var serialize = function() {
	buf = "<criteria>";
	$('.criterion').each(function(i,e) {
	    buf += "<criterion type='enum' code='";
	    buf += $(e).find('.panel-heading input').val();
	    buf += "'>"
	    $(e).find('.panel-body input').each(function(j,v) {
		buf += "<value>"
		buf += $(v).val();
		buf += "</value>";
	    })
	    buf += "</criterion>";

	});
	buf += "</criteria>";
	return buf;
    }
    
    $('#btn_save').on('click', function(e){
	$.ajax({
	    url:'/settings/criteria',
	    type:'POST',
	    data:serialize(),
	    contentType:'text/xml'
	}).success(function(data) {
	    $('#btn_save').addClass('disabled');
	    $('#btn_save').addClass('btn-default');
	    $('#btn_save').removeClass('btn-warning');
	});
    });

    var new_value = function(ref) {
	ref.before(
	    $('<div>',{
		'class':"row",
		'html':[
		    $('<div>',{
		    'class':"col-md-8",
			'html':$('<input>',{
			    'type':"text",
			    'class':"form-control",
			    'value':""})
		    }),
		    $('<div>',{
			'class':"col-md-4",
			'html':$('<button>',{
			    'class':"btn btn-default btn-xs crit-del-value",
			    'html':'Supprimer'})
		    })
		]})
	);
    }

    var new_criterion = function() {
	var id = $('.criterion').length + 1
	$('.criterion').last().after(
	    $('<div>',{ 
		'class':"criterion",
		'html':
		$('<div>',{ 
		    'class':"panel panel-default",
		    'html':[
			$('<div>',{
			    'class':"panel-heading",
			    'html':[
				$('<a>',{
				    'data-toggle':"collapse", 
				    'href':"#collapse_"+id,
				    'html':[
					$('<small>',{
					    'data-ui':"yes",
					    'html':[
						$('<span>', { 
						    'class':"glyphicon glyphicon-chevron-right", 
						    'aria-hidden':"true"}),
						$('<span>', {
						    'class':"glyphicon glyphicon-chevron-down",
						    'aria-hidden':"false"})]
					}),
					$('<input>', {
					    'type':"text",
					    'value':""})]
				}),
				$('<span>', {
				    'class':"pull-right",
				    'html':$('<button>',{ 
					'type':"button", 
					'class':"btn btn-default btn-xs crit-del-crit",
					'html':'Supprimer'})
				})]
			}),
			$('<div>',{
			    'class':"panel-collapse collapse in",
			    'id':"collapse_"+id,
			    'html':$('<div>',{
				'class':"panel-body",
				'html':[
				    $('<strong>',{'html':'Valeurs'}),
				    $('<div>',{
					'class':"row top-margin",
					'html':$('<div>', { 
					    'class':"col-sm-12",
					    'html':$('<button>',{
						'class':"btn btn-default btn-xs crit-add-value",
						'html':'Ajouter une valeur'})
					})
				    })]
			    })
			})
		    ]})
	    })
	);
	new_value($('.criterion .crit-add-value').closest('div.row').last())
    }


    $('body').on('click','.crit-add-value', function(e) {
	new_value($(this).closest('div.row'));
	enable_save();
    });

    $('body').on('click','.crit-del-value', function(e) {
	$(this).closest('div.row').remove();
	enable_save();
    });

    $('body').on('click','.crit-add-crit', function(e) {
	new_criterion();
	enable_save();
    });

    $('body').on('click','.crit-del-crit', function(e) {
	$(this).closest('div.panel').remove();
	enable_save();
    });

    $('body').on('change','input', function(e) {
	enable_save();
    });
});