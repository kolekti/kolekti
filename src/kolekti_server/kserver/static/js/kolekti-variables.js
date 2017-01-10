$(document).ready(function() {
    var conditions = kolekti_variable_data['conditions'];
    var criteria = kolekti_variable_data['criteria'];
    var variables = kolekti_variable_data['variables'];
    var path = $('#main').data('path');

    // add condition 
    
    var exists_condition = function(togglefct) {
	togglefct(false);
	var exists = false;
	$.each(conditions, function(i,v){
//	    console.log(i,v);
	    var matched = true;
	    $(".crit-menu").each( function(ci, cv) {
//		console.log('crit-menu', $(cv).data('crit'))
		var crit = $(cv).data('crit')
//		console.log($(cv).data('value'))
//		console.log(v['expr'][crit])
		if (v['expr'][crit] != $(cv).data('val'))
		    matched = false;
	    });
	    matched && togglefct(true);
	});
    }


    var toggle_cond = function(status){
//	console.log('toggle', status)
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
	$(this).closest('.btn-group').find('.valuelabel').html($(this).data('valuelabel'))
	$(this).closest('.btn-group').data('val', $(this).data('valuelabel'))
	$(this).closest('.btn-group').find('button').val($(this).data('valuelabel'))
	exists_condition(toggle_cond)
    })

    $('#modal_cond').on('show.bs.modal', function (e) {
	if($(e.relatedTarget).hasClass('kolekti-action-edit-condition')){
	    var index = $(e.relatedTarget).data('condindex') - 1;
	    $('#cond_index').val(index + 1)
	    $('#cond_action').val('editcond')
	    $(this).find('.crit-menu').each(function(i,menu) {
		console.log($(menu).data('crit'))
		var iv = conditions[index]['expr'][$(menu).data('crit')]
		console.log(conditions[index]['expr'])
		$(menu).data('val', iv)
		$(menu).find('.valuelabel').html(iv)
		$(menu).find('button').val(iv)
	    });
	    $('#alert_cond_exists').hide();
	    $('#cond_save').addClass('disabled');
	} else {
	    $('#cond_action').val('newcond')
	    $(this).find('.crit-menu').each(function(i,menu) {
		var iv = $(menu).find('li a').first().data('valuelabel')
		$(menu).data('val', iv)
		$(menu).find('.valuelabel').html(iv)
		$(menu).find('button').val(iv)
	    });
	    exists_condition(toggle_cond)
	}
    })
    

    $('#modal_cond form').on('submit', function() {
	// check
	$(this).find('.crit-menu').each(function(i,menu) {
	    console.log( $(menu).data('crit'),$(menu).data('val'));
	    $("<input>")
		.attr("type", "hidden")
		.attr("name", $(menu).data('crit'))
		.attr("value", $(menu).data('val'))
		.appendTo($('#modal_cond form'))
	})
    })

    

    var add_crit_build_val_menu = function() {
//	console.log('val menu')
	var crit = $('#crit_cond_menu').data('val')
//	console.log(crit)
	$("#crit_val_menu ul").html('')
//	console.log('iter', criteria[crit])
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
		$('#crit_val_menu').find('button').val(v)
	    }
	});

    }

    $('#modal_add_crit .crit_cond_item').on('click', function() {
	// condition menu
	$(this).closest('.btn-group').find('.valuelabel').html($(this).data('valuelabel'))
	$(this).closest('.btn-group').data('val', $(this).data('valuelabel'))
	$(this).closest('.btn-group').find('button').val($(this).data('valuelabel'))
	add_crit_build_val_menu()
    })

    $('#modal_add_crit').on('click', '.crit_val_item', function() {
	// value  menu
	$(this).closest('.btn-group').find('.valuelabel').html($(this).data('valuelabel'))
	$(this).closest('.btn-group').data('val', $(this).data('valuelabel'))
	$(this).closest('.btn-group').find('button').val($(this).data('valuelabel'))
    })

    
    $('#modal_add_crit').on('show.bs.modal', function (e) {
	$(this).find('#crit_cond_menu').each(function(i,menu) {
	    var iv = $(menu).find('li a').first().data('valuelabel')
	    $(menu).data('val', iv)
	    $(menu).find('.valuelabel').html(iv)
	    $(menu).find('button').val(iv)
	});
	add_crit_build_val_menu();
    })
    
    
    $('#modal_add_crit form').on('submit', function() {
	$(this).find('.btn-group-add-crit').each(function(i,menu) {
	    $("<input>")
		.attr("type", "hidden")
		.attr("name", $(menu).data('crit'))
		.attr("value", $(menu).data('val'))
		.appendTo($('#modal_add_crit form'))
	})
    })
    
    $('.kolekti-action-remove-variable').on('click', function() {
	var varindex = $(this).data('varindex')
	var varname = $(this).data('varname')
	if (confirm('Voulez vous réélement supprimer la variable '+varname)) {
	    $.ajax({
		url:'/variables/detail/',
		type:'POST',
		data:{"action":"delvar",
		      "path":path,
		      "index":varindex}
	    }).success(function(data) {
		window.location.href='/variables/detail/?path='+path
	    });
	}
	
    })

    $('#modal_new_variable').on('show.bs.modal', function (e) {
	$('#var_newvar').focus()
    })

    $('#modal_rename_variable').on('show.bs.modal', function (e) {
	var index = $(e.relatedTarget).data('varindex');
	$('#var_rename_index').val(index)
	$('#input_rename').val(variables[index - 1])
	$('#input_rename').focus()
    })

    
    
    $('.kolekti-action-remove-condition').on('click', function() {
	var condindex = $(this).data('condindex')
	var condname = $(this).data('condname')
	if (confirm('Voulez vous réélement supprimer toutes les valeurs pour la condition  '+condname)) {
	    $.ajax({
		url:'/variables/detail/',
		type:'POST',
		data:{"action":"delcond",
		      "path":path,
		      "index":condindex}
	    }).success(function(data) {
		window.location.href='/variables/detail/?path='+path
	    });
	}
	
    })
    
    

});
