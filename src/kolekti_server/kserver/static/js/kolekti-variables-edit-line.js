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
	    url:'/variables/editvar/',
	    type:'POST',
	    data:JSON.stringify(data),
	    contentType:'text/javascript'
	}).success(function(data) {
	    disable_save()
	    kolekti_recent(displayname(kolekti_variable_path),'variables','/variables/editvar/?path='+kolekti_variable_path);
	});
    });

    
    var current = kolekti_variable_current 

    var record_values = function() {
	$('.varedit input.varinput').each(function(i,v) {
	    kolekti_variable_data["values"][current][i] = $(this).val();
	});	
    }
    
    var init_ui = function() {
	$('.label-current').html(kolekti_variable_data["variables"][current]);
	if (current == 0) {
	    $('.variable-previous').hide();
	} else {
	    $('.variable-previous').show();
	    $('.label-previous').html(kolekti_variable_data["variables"][current - 1]);
	}
	if (current == (kolekti_variable_data["variables"].length - 1)) {
		$('.variable-next').hide();
	} else {
	    $('.variable-next').show();
	    $('.label-next').html(kolekti_variable_data["variables"][current + 1]);
	}
	    	
	$('.varedit input.varinput').each(function(i,v) {
	    $(this).val(kolekti_variable_data["values"][current][i]);
	    
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



