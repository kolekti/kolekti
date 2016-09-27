
$(document).ready(function() {

    // save button state
    
    var enable_save = function() {
	$('#btn_save').removeClass('disabled');
	$('#btn_save').removeClass('btn-default');
	$('#btn_save').removeClass('hidden');
	$('#btn_save').addClass('btn-warning');
    }

    var disable_save = function() {
	$('#btn_save').addClass('disabled');
	$('#btn_save').addClass('btn-default');
	$('#btn_save').removeClass('btn-warning');
    }


    $(window).on('beforeunload', function(e) {
	if($('#btn_save').hasClass('btn-warning')) {
            return 'Trame non enregistrée';
	}
    });

    // save action
    
    $('#btn_save').on('click', function() {
	$.ajax({
	    url:'/projects/config',
	    type:'POST',
	    dataType: 'json',
	    data:data()
	}).success(function(data) {
	    disable_save()
	});
    })

    // language menus
    
    $(document).on('click','.lang_del',function() {
	if (! $(this).closest('.btn-lang').find('a.btn').hasClass('btn-info')) {
	    $(this).closest('.btn-lang').remove()
	    enable_save()
	}
    })
    $(document).on('click','.lang_add',function() {
	var new_lang = $(this).closest('.btn-lang-group').find('input').val()
	var langs =  $(this).closest('.btn-lang-group').find('.lang').map( function() { return $(this).html()}) 
	if($.inArray(new_lang,langs) < 0) {
	    var $lang = $(this).closest('.btn-lang-group').find('.btn-group.hidden').last()
	    var $new = $lang.clone()
	    $new.insertBefore($lang)
	    $new.removeClass('hidden')
	    $new.addClass('btn-lang')
	    $new.find('.lang').html(new_lang)
	    enable_save()
	    $(this).closest('.btn-lang-group').find('input').val('')
	    $(this).closest('.btn-lang-group').find('input').focus()
	}
    })
    
    $(document).on('click','.lang_default',function() {
	$(this).closest('.btn-lang-group').find('li.disabled').removeClass('disabled')
	$(this).closest('.btn-lang-group').find('a.btn-info').removeClass('btn-info')
	$(this).closest('.btn-lang').find('li').addClass('disabled')
	$(this).closest('.btn-lang').find('a.btn').addClass('btn-info')
	enable_save()
    })


    var data = function() {
	return {
	    'sources':$.makeArray($('#edit_langs').find('.btn-lang .lang').map( function() { return $(this).html()})),
	    'default_source':$('#edit_langs').find('a.btn-info .lang').html(),
	    'releases':$.makeArray($('#release_langs').find('.btn-lang .lang').map( function() { return $(this).html()}))
	}
    }
})
