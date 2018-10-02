
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
	    var url = Urls.kolekti_languages_edit(kolekti.project)
        console.log(url)
	    $.post(url, data())
            .done(function(data) {
	            disable_save()
	        });
    })

    // language menus
    
    $(document).on('click','.lang-del',function() {
	    if (!($(this).closest('.lang').data('defaut') == 'yes')) {
	        $(this).closest('.lang').remove()
	        enable_save()
	    } else {
            alert('foo')
        }
    })
    
    $(document).on('click','.lang_add',function() {
	    var new_label = $(this).closest('tr').find('input.klabel').val()
	    var new_code = $(this).closest('tr').find('input.kcode').val()
        if (!(new_label.length && new_code.length)) {
            alert('Entrez une langue et un code')
            return
        }
        
	    var langs =  $(this).closest('.table').find('.lang-code').map( function() { return $(this).html()}) 
	    if($.inArray(new_code,langs) < 0) {
	        var $lang = $(this).closest('.table').find('tbody tr').last()
	        var $new = $lang.clone()
	        $new.insertAfter($lang)
	        $new.find('.lang-code').html(new_code)
	        $new.find('.lang-label').html(new_label)
	        enable_save()
	        $(this).closest('.tr').find('input').val('')
	        $(this).closest('.tr').find('input').first().focus()
	    } else {
            alert('Ce code existe déjà')
            return
        }
    })
    
    $(document).on('click','.lang_default',function() {
	    $(this).closest('table').find('.lang').data('default', null)
	    $(this).closest('table').find('.lang-del').removeClass('disabled')
        $(this).closest('.lang').data('default', 'yes')
	    $(this).closest('.lang').find('.lang-del').addClass('disabled')
	    enable_save()
    })


    var data = function() {
	    return {
	        'sources':$.makeArray($(document).find('.lang').map( function() {
                return $(this).find('.lang-code').html() + ':' + $(this).find('.lang-label').html()
                })),
	        'default_source':$(document).find('.lang').filter(function(i,e){return $(e).data('default') == 'yes'}).find('.lang-code').html()
	    }
    }
})
