$(document).ready(function() {
    var conditions = kolekti_variable_data['conditions'];
    var criteria = kolekti_variable_data['criteria'];
    var path = $('#main').data('path');

    // add condition 
    
    var exists_condition = function(togglefct) {
	togglefct(false);
	var exists = false;
	$.each(conditions, function(i,v){
	    console.log(i,v);
	    var matched = true;
	    $(".crit-menu").each( function(ci, cv) {
		console.log('crit-menu', $(cv).data('crit'))
		var crit = $(cv).data('crit')
		console.log($(cv).data('value'))
		console.log(v['expr'][crit])
		if (v['expr'][crit] != $(cv).data('val'))
		    matched = false;
	    });
	    matched && togglefct(true);
	});
    }


    var toggle_cond = function(status){
	console.log('toggle', status)
	if(status) {
	    $('#alert_cond_exists').show();
	    $('#cond_save').addClass('disabled')
	} else {
	    $('#alert_cond_exists').hide();
	    $('#cond_save').removeClass('disabled');
	}
    }
    
    $('#modal_cond .cond_item').on('click', function() {
	// condition menu
	console.log($(this).data('valuelabel'))
	console.log($(this).closest('.btn-group'));
	$(this).closest('.btn-group').find('.valuelabel').html($(this).data('valuelabel'))
	$(this).closest('.btn-group').data('val', $(this).data('valuelabel'))
	exists_condition(toggle_cond)
    })

    $('#modal_cond').on('show.bs.modal', function (e) {
	$(this).find('.crit-menu').each(function(i,menu) {
	    var iv = $(menu).find('li a').first().data('valuelabel')
	    $(menu).data('val', iv)
	    $(menu).find('.valuelabel').html(iv)
	})
	exists_condition(toggle_cond)
    })
    


    var add_crit_build_val_menu = function() {
	console.log('val menu')
	var crit = $('#crit_cond_menu').data('val')
	console.log(crit)
	$("#crit_val_menu ul").html('')
	console.log('iter', criteria[crit])
	$.each(criteria[crit], function(i,v){
//	    console.log('menu val',v)
	    $("#crit_val_menu ul").append(
		$('<li>',{
		    'html':$('<a>', {
			'class':"crit_val_item",
			'data-valuelabel':v,
			'href':"#",
			'html':v
		    })
		})
	    )
	    if (i==0) {
		$('#crit_val_menu').find('.valuelabel').html(v)
		$('#crit_val_menu').data('val', v)
	    }
	});

    }

    $('#modal_add_crit .crit_cond_item').on('click', function() {
	// condition menu
	$(this).closest('.btn-group').find('.valuelabel').html($(this).data('valuelabel'))
	$(this).closest('.btn-group').data('val', $(this).data('valuelabel'))
	add_crit_build_val_menu()
    })

    $('#modal_add_crit').on('click', '.crit_val_item', function() {
	// value  menu
	$(this).closest('.btn-group').find('.valuelabel').html($(this).data('valuelabel'))
	$(this).closest('.btn-group').data('val', $(this).data('valuelabel'))
    })

    
    $('#modal_add_crit').on('show.bs.modal', function (e) {
	$(this).find('#crit_cond_menu').each(function(i,menu) {
	    var iv = $(menu).find('li a').first().data('valuelabel')
	    $(menu).data('val', iv)
	    $(menu).find('.valuelabel').html(iv)
	});
	add_crit_build_val_menu();
    })
    
    $('#modal_cond form').on('submit', function() {
	// check
    })
    
    $('#modal_add_crit form').on('submit', function() {
	// check
    })
    
    $('.kolekti-action-remove-variable').on('click', function() {
	var varindex = $(this).data('varindex')
	var varname = $(this).data('varname')
	if (confirm('Voulez vous réélement supprimer la variable '+varname)) {
	    $.ajax({
		url:'/variables/detail/',
		type:'POST',
		data:{"action":"dellvar",
		      "path":path,
		      "index":varindex}
	    }).success(function(data) {
		window.location.href='/variables/detail/?path='+path
	    });
	}
	
    })
    
    

});
