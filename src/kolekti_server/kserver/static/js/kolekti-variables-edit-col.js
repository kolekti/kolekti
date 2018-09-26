$(function() {

    var enable_save = function() {
	$('#btn_save').removeClass('disabled');
	$('#btn_save').removeClass('btn-default');
	$('#btn_save').addClass('btn-warning');
    }
    
    var disable_save = function() {
	$('#btn_save').addClass('disabled');
	$('#btn_save').addClass('btn-default');
	$('#btn_save').removeClass('btn-warning');
    }

    $(window).on('beforeunload', function(e) {
	if($('#btn_save').hasClass('btn-warning')) {
            return 'Modifications non enregistrées';
	}
    });
    
    $('#btn_save').on('click', function() {
	    record_values();
	    var data = { "path":kolekti_variable_path,
		             "data":kolekti_variable_data["values"]
		           }
	    
	    $.ajax({
	        url:Urls.kolekti_variable_editcol(kolekti.project, kolekti.lang, kolekti_variable_path),
	        type:'POST',
	        data:JSON.stringify(data),
	        contentType:'text/javascript'
	    }).success(function(data) {
	        disable_save()
            var lang = kolekti_variable_path.split('/')[2]
            var variable_path = kolekti_variable_path.split('/').splice(4). join('/')
	        kolekti_recent(displayname(kolekti_variable_path),
                           'variables',
                           Urls.kolekti_variable(kolekti.project, lang, variable_path))
	    });
    });

    
    var current = kolekti_variable_current 

    var record_values = function() {
	$('.varedit input.varinput').each(function(i,v) {
	    kolekti_variable_data["values"][i][current] = $(this).val();
	});	
    }
    
    var init_ui = function() {
	$('.label-current').html(kolekti_variable_data["conditions"][current]["label"]);
	if (current == 0) {
	    $('.variable-previous').hide();
	} else {
	    $('.variable-previous').show();
	    $('.label-previous').html(kolekti_variable_data["conditions"][current - 1]["label"]);
	}
	if (current == (kolekti_variable_data["conditions"].length - 1)) {
	    $('.variable-next').hide();
	} else {
	    $('.variable-next').show();
	    $('.label-next').html(kolekti_variable_data["conditions"][current + 1]["label"]);
	}
	    	
	$('.varedit input.varinput').each(function(i,v) {
	    $(this).val(kolekti_variable_data["values"][i][current]);
	    
	});
	$('.varedit input.varinput').first().focus();
    }

    init_ui();

    $(".variable-next button").on("click", function() {
	record_values();
	current++;
	init_ui();
    })
    
    $(".variable-previous button").on("click", function() {
	record_values()
	current--;
	init_ui();
    })

    $('.varedit input.varinput').on('change', enable_save);
    
})



