$(document).ready(function() {

    var enable_save = function() {
	$('#btn_save').removeClass('disabled');
	$('#btn_save').removeClass('btn-default');
	$('#btn_save').removeClass('hidden');
	$('#btn_save').addClass('btn-warning');
    }

    var serialize = function() {
	buf = "<job id='";
	buf += $('#job_id').html();
	buf += "'>";
	buf += "<dir value='"+$('#job_id').html()+"'/>";

	// pre assembly filters
	buf += "<criteria>";
	$("#crit_assembly .kolekti-crit").each(function(i,e) {
	    var val = $(e).data('kolekti-crit-value');
	    if (val != '') {
		buf += "<criterion code='"+ $(e).data('kolekti-crit-code') +"' value='"+ val +"'/>" ;
	    }
	});
	buf += "</criteria>";

	// profiles
	buf += "<profiles>";
	$("#job_body .profile").each(function(i,e) {
	    buf += "<profile enabled='";
	    if ($(e).find('.profile-enabled').get(0).checked) {
		buf += "1"
	    } else {
		buf += "0"
	    }
	    buf += "'>";
	    buf += "<label>" + $(e).find('.profile-name').val() + "</label>";
	    buf += "<dir value='" + $(e).find('.profile-dir').val() + "'/>";
	    buf += "<criteria>";
	    $(e).find(".kolekti-crit").each(function(i,c) {
		var val = $(c).data('kolekti-crit-value');
		if (val == '*') {
		    buf += "<criterion code='"+ $(c).data('kolekti-crit-code') +"'/>" ;
		}
		else if (val != '') {
		    buf += "<criterion code='"+ $(c).find('.kolekti-crit-code').html() +"' value='"+ val +"'/>" ;
		}
	    });
	    buf += "</criteria>";
	    buf += "</profile>";
	});
	buf += "</profiles>";
	buf += "<scripts>";
	$("#job_body .script").each(function(i,e) {
	    buf += "<script name='"+$(e).data("kolekti-script-id")+"' enabled='";
	    if ($(e).find('.script-enabled').get(0).checked) {
		buf += "1"
	    } else {
		buf += "0"
	    }
	    buf += "'>"
	    var suffix = $(e).find('.script-suffix').val();
	    if (suffix.length) {
		buf +='<suffix enabled="1">'+suffix+'</suffix>';
	    } else {
		buf +='<suffix enabled="0"/>';
	    }
	    buf += "<parameters>";
	    $(e).find(".script-parameter").each(function(i,s) {
		var name=$(s).data('script-param-name');
		var type=$(s).data('script-param-type');
		var value;
		if (type == "filelist") {
		    value = $(s).data('kolekti-param-value');
		}
		if (type == "boolean") {
		    if($(s).find('.kolekti-crit-value').get(0).checked)
			value = 'yes';
		    else
			value='no';
		}
		
		buf += "<parameter name='"+name+"' value='"+ value +"'/>";
	    });
	    buf += "</parameters>";
	    buf += "</script>";
	});
	buf += "</scripts>";
	buf += "</job>";
	return buf;
    };

    $('#btn_save').on('click', function(e){
	$.ajax({
	    url:'/settings/job?path='+$(this).data('path'),
	    type:'POST',
	    data:serialize(),
	    contentType:'text/xml'
	}).success(function(data) {
	    $('#btn_save').addClass('disabled');
	    $('#btn_save').addClass('btn-default');
	    $('#btn_save').addClass('hidden');
	    $('#btn_save').removeClass('btn-warning');
	});
    });
    
    // click on criteria  menu 
    $('.crit-val-menu-entry').on('click', function(e) {
	var value = $(this).data('kolekti-crit-value');
	$(this).closest('.btn-group').find('.kolekti-crit-value-menu').html($(this).html());
	$(this).closest('.kolekti-crit').data('kolekti-crit-value',$(this).data('kolekti-crit-value'));
	update_filters();
	e.preventDefault();
	enable_save();
    });

    // click on script parameter menu entry 
    $('.script-param-menu-entry').on('click', function(e) {
	var value = $(this).data('kolekti-param-value');
	$(this).closest('.btn-group').find('.kolekti-param-value-menu').html($(this).html());
	$(this).closest('.kolekti-crit').data('kolekti-param-value',$(this).data('kolekti-param-value'));
	e.preventDefault();
	enable_save();
    });

    // click on suppress profile / script button
    $('.suppr').on('click', function(e) {
	$(this).closest('.profile').remove()
	$(this).closest('.script').remove()
	e.preventDefault();
	enable_save();
    })

    // change any text field
    $('#job_body input[type=text]').on('change', function(e) {
	enable_save();
    })

    // click on active script or profile
    $('.script-enabled').on('click', function(e) {
	enable_save();
    })

    $('.profile-enabled').on('click', function(e) {
	enable_save();
    })


    //click on add profile
    $('#btn_add_profil').on('click', function(e) {
	$('#job_profiles .profile').last().after(
	    $('.job-templates .profile').clone(true)
	)
	update_filters();
	$('#job_profiles .profile').last().find('input').first().focus();
	$('#job_profiles .profile').last().find('.profile-enabled').first().prop( "checked", true );
	e.preventDefault();
	enable_save();
    });

    //click on add script item
    $('.script-menu-item').on('click', function(e) {
	var script = $(this).data('kolekti-script-id');
	$('#job_scripts .script').last().after(
	    $('.job-templates .'+script).clone(true)
	)
	$('#job_scripts .script').last().find('input').first().focus();
	$('#job_scripts .script').last().find('.kolekti-param-menu').each(function(i,e) {
	    var ev = jQuery.Event( "click" );
	    $(e).find(".script-param-menu-entry").first().trigger(ev);
	})
	e.preventDefault();
	enable_save();

    });

    var update_filters = function() {
	var prefilters = {};
	$('#crit_assembly .kolekti-crit').each(function(i, e) {
	    var critcode = $(e).data('kolekti-crit-code');
	    prefilters[$(e).data('kolekti-crit-code')] = $(e).data('kolekti-crit-value')
	});
	$('.profile .kolekti-crit').each(function(i,e) {
	    if( prefilters.hasOwnProperty($(e).data('kolekti-crit-code')) &&
		prefilters[$(e).data('kolekti-crit-code')] != "") {
		$(e).addClass('disabled');
		$(e).find('button').addClass('disabled');
	    } else {
		$(e).removeClass('disabled');
		$(e).find('button').removeClass('disabled');
	    }
	});
    };
    update_filters();
})