$(document).ready(function() {

    var enable_save = function() {
	$('#btn_save').removeClass('disabled');
	$('#btn_save').removeClass('btn-default');
	$('#btn_save').addClass('btn-warning');
    }

    $(window).on('beforeunload', function(e) {
	if($('#btn_save').hasClass('btn-warning')) {
            return 'Paramètres non enregistrés';
	}
    });

    var serialize = function() {
	buf = "<job>";
//	id='";
//	buf += $('#job_id').html();
//	buf += "'>";
//	buf += "<dir value='"+$('#job_id').html()+"'/>";

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
		if (!$(c).hasClass('disabled')) {
		    var val = $(c).data('kolekti-crit-value');
		    if (val == '*') {
			buf += "<criterion code='"+ $(c).data('kolekti-crit-code') +"'/>" ;
		    }
		    else if (!(val === '')) {
			buf += "<criterion code='"+ $(c).find('.kolekti-crit-code').html() +"' value='"+ val +"'/>" ;
		    }
		}
	    });
	    buf += "</criteria>";
	    buf += "</profile>";
	});
	buf += "</profiles>";
	buf += "<scripts>";
	$("#job_scripts>.script").each(function(i,e) {
	    buf += "<script name='"+$(e).data("kolekti-script-id")+"' enabled='";
	    if ($(e).find('.script-enabled').get(0).checked) {
		buf += "1"
	    } else {
		buf += "0"
	    }
	    buf += "'>"
	    var label = $(e).find('.script-name').val();
	    buf +='<label>' + label + '</label>';
	    var filename = $(e).find('.script-filename').val();
	    buf +='<filename>' + filename + '</filename>';
	    if ($(e).find('.publication-scripts .script').length || $(e).find('.validation-scripts .script').length) {
		buf += "<publication>";
		$(e).find('.publication-scripts .script').each(function(i,pe) {
		    buf += "<script name='"+$(pe).data("kolekti-script-id")+"'>";
		    buf += serialize_script_params(pe);
		    buf += "</script>";
		});
		buf += "</publication>";
		buf += "<validation>";
		$(e).find('.validation-scripts .script').each(function(i,pe) {
		    buf += "<script name='"+$(pe).data("kolekti-script-id")+"'>";
		    buf += serialize_script_params(pe);
		    buf += "</script>";
		});
		buf += "</validation>";
	    } else {
		buf += serialize_script_params(e)
	    }
	    buf += "</script>";
	});
	buf += "</scripts>";
	buf += "</job>";
	return buf;
    };

    var serialize_script_params = function(e) {
	var buf = "<parameters>";
	$(e).find(".script-parameter").each(function(i,s) {
	    var name=$(s).data('script-param-name');
	    var type=$(s).data('script-param-type');
	    var value;
	    if (type == "filelist") {
		value = $(s).data('kolekti-param-value');
	    }
	    if (type == "text") {
		value = $(s).find('.kolekti-crit-value').val();
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
	return buf
    }
    
    $('#btn_save').on('click', function(e){
	var path = $(this).data('path');
	$.ajax({
	    url:Urls.kolekti_job_edit(kolekti.project, path),
	    type:'POST',
	    data:serialize(),
	    contentType:'text/xml'
	}).success(function(data) {
	    $('#btn_save').addClass('disabled');
	    $('#btn_save').addClass('btn-default');
	    $('#btn_save').removeClass('btn-warning');
	    kolekti_recent(displayname(path), 'paramètres', '/settings/job?path='+path)

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
	$(this).closest('.script-parameter').data('kolekti-param-value',value);
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
    $('#job_body').on('change', 'input', function(e) {
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
	$('#job_profiles').append(
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
	$('#job_scripts').append(
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

    //click on add script item in pultiscript
    $('.multi-menu-item').on('click', function(e) {
	var script = $(this).data('kolekti-script-id');
	var multi = $(this).closest('.multi-area').find('.multiscript-list');
	console.log(multi)
	multi.append(
	    $('.job-templates .'+script).clone(true)
	)
	multi.find('.script').last().find('input').first().focus();
	multi.find('.script').last().find('.kolekti-param-menu').each(function(i,e) {
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
