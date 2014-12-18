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
	buf += "<criteria>";
	$("#crit_assembly .kolekti-crit").each(function(i,e) {
	    var val = $(e).find('.kolekti-crit-value-menu').html();
	    if (val != 'non filtré') {
		buf += "<criterion code='"+ $(e).find('.kolekti-crit-code').html() +"' value='"+ val +"'/>" ;
	    }
	});
	buf += "</criteria>";
	buf += "<profiles>";
	$(".profile").each(function(i,e) {
	    buf += "<profile enabled='1'>";
	    buf += "<label>" + $(e).find('.profile-name').val() + "</label>";
	    buf += "<dir value='" + $(e).find('.profile-dir').val() + "'/>";
	    buf += "<criteria>";
	    $(e).find(".kolekti-crit").each(function(i,c) {
		var val = $(c).find('.kolekti-crit-value-menu').html();
		if (val != 'non filtré') {
		    buf += "<criterion code='"+ $(c).find('.kolekti-crit-code').html() +"' value='"+ val +"'/>" ;
		}
	    });
	    buf += "</criteria>";
	    buf += "</profile>";
	});
	buf += "</profiles>";
	buf += "<scripts>";
	$(".script").each(function(i,e) {
	    buf += "<script name='"+$(e).data("kolekti-script-id")+"' enabled='1'>"
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
		    value = $(s).find('.kolekti-crit-value-menu').html()
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
    
    $('.crit-val-menu-entry').on('click', function(e) {
	$(this).closest('.btn-group').find('.kolekti-crit-value-menu').html($(this).html())
	e.preventDefault();
	enable_save();
    });

    $('.suppr').on('click', function(e) {
	$(this).closest('.profile').remove()
	$(this).closest('.script').remove()
	e.preventDefault();
	enable_save();
    })
})