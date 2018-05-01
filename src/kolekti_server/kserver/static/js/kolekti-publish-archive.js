$(function(){


    var get_publish_languages = function() {
        return $("li.lang").map(function(){return $(this).data('lang')}).get()
    }
    
    $('.btn_publish').on('click', function() {
	    var url='/releases/publish/'
        
	    $('<div class="panel panel-default"><div class="panel-heading"><h4 class="panel-title">Publication de la version</h4></div><div class="panel-body"><div class="progress" id="pub_progress"><div class="progress-bar progress-bar-striped active"  role="progressbar" aria-valuenow="100" aria-valuemin="0" aria-valuemax="100" style="width: 100%"><span class="sr-only">Publication in progress</span></div></div><div id="pub_results"></div><div id="pub_end" class="alert alert-info" role="alert">Publication terminée</div></div></div>').appendTo($('#pubresult'));
	    //params = get_publish_params(job)

	    $('#pub_end').hide();
	    
	    var params = {}
	    var release = $('#main').data('release')
	    params['release']=release;
	    params['langs']= get_publish_languages();
	    var streamcallback = function(data) {
	        $("#pub_results").html(data);
	    }
	
	    $.ajaxPrefilter("html streamed", function(){return "streamed"});
	    streamedTransport(streamcallback);
	    $.ajax({
	        url:url,
	        type:'POST',
	        data:params,
	        dataType:"streamed",
	        beforeSend:function(xhr, settings) {
		        ajaxBeforeSend(xhr, settings);
		        settings.xhr.onreadystatechange=function(){
		            console.log(xhr.responseText);
		        }
	        }
	    }).done(function(data) {
	        $("#pub_results").html(data);
	    }).fail(function(jqXHR, textStatus, errorThrown) {
	        $('#pub_results').html([
		$('<div>',{'class':"alert alert-danger",
			       'html':[$('<h5>',{'html':"Erreur"}),
				           $('<p>',{'html':"Une erreur inattendue est survenue lors de la publication"})
				           
				          ]}),
		        $('<a>',{
		            'class':"btn btn-primary btn-xs",
		            'data-toggle':"collapse",
		            'href':"#collapseStacktrace",
		            'aria-expanded':"false",
		            'aria-controls':"collapseStracktrace",
		            'html':'Détails'}),
		        $('<div>',{'class':"well",
			               'html':[
			                   $('<p>',{'html':textStatus}),
			                   $('<p>',{'html':errorThrown}),
			                   $('<pre>',{'html':jqXHR.responseText})]
			              })
	        ]);
	    }).always(function() {
	        $('#pub_progress').remove();
	        $('#pub_end').show();
            $('#pub_before').remove();
	    });
    })
})
