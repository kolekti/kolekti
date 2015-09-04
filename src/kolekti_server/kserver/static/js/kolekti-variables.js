$(document).ready(function() {

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
    
    var path = $('#btn_save').data('path');
    var nbvar = 0;
    
    var serialize = function() {
<<<<<<< HEAD
=======
	buf = "<variables><critlist>";
	
>>>>>>> dev
	var conditions = [];
	$('#main thead tr[data-crit]').first().find('th.critval').each(function(i,cell) {
	    valconds = "";
	    $('#main thead tr[data-crit]').each(function(j,row) {
		var critname = $(row).data('crit')
		var critval = $($(row).find('th.critval')[i]).find('span').first().html();
		valconds += '<crit name="'+ critname +'" value="' + critval + '"/>';
<<<<<<< HEAD
	    });
	    conditions.push(valconds)
	});

	buf = "<variables>";
=======
		if(i==0)
		    buf += '<crit>:'+critname+'</crit>';
	    });
	    conditions.push(valconds)
	});
	buf += '</critlist>';
	
>>>>>>> dev
	$('#main tbody tr').each(function(i, row) {
	    var varname = $(row).find('th').first().find('span').first().html();
	    buf +='<variable code="' + varname + '">';
	    $(row).find('td').each(function(j,cell) {
		var varval = $(cell).find('span').first().html();
		buf +='<value>'
		buf += conditions[j]
		buf += '<content>' + varval + '</content>'
		buf += '</value>'
	    });
	    buf += "</variable>";
	});
	buf += "</variables>"
	return buf;
    }


    
    $('#btn_save').on('click', function(e){
	$.ajax({
	    url:'/variables/detail/?path='+path,
	    type:'POST',
	    data:serialize(),
	    contentType:'text/xml'
	}).success(function(data) {
	    disable_save()
	});
    });
    
    var criteria;

    $.get('/settings.json').success(
	function(data) {
	    var langs = data['srclangs'];
	    $.get('/criteria.json').success(
		function(data) {
		    criteria = data
		    criteria['LANG']=langs;
		    $('#list_add_crit').html($.map(Object.keys(criteria), function(c) {
			return $('<li>', {
			    'html':$('<a>', {
				'data-crit':c,
				'class':'item_add_crit item_add_crit_'+c,
				'html':c
			    })
			})
		    }));
		    $.get(path).success(
			function(data) {
			    $('#main thead').append($('<tr>',{
				'class':'colheaders',
				'id':'colheaders',
				'html':$('<td>')}));
			    $(data).find('variable').first().each(function(a,v) {
				var val=$(v).find('value').first();
				val.find('crit').each(function(i,e) {
				    disable_add_crit($(e).attr('name'))
				    $('#main thead').append($('<tr>',{
					'id':'crit_'+$(e).attr('name'),
					'data-crit':$(e).attr('name'),
					'class':'info',
					'html':$('<th>',{
					    'class':'critname',
					    'html':$('<span>',{
						'html':$(e).attr('name')
					    })
					})
				    }))
				});
				$(v).find('value').each(function(i,value) {
				    $('#colheaders').append($('<td>',{
					'class':'colheader',
					'html':ui_col_header()
				    }));

				    $(value).find('crit').each(function(j,e){
					$('#crit_'+$(e).attr('name')).append(
					    $('<th>',{
						'class':'critval',
						'data-crit':$(e).attr('name'),
						'html':$('<span>',{
						    'html':$(e).attr('value')})
					    })
					)
				    });
				});
			    });
			    $(data).find('variable').each(function(a,variable) {
				nbvar++;
				$('#main tbody').append($('<tr>',{
				    'id':'var_'+nbvar,
				    'html':$('<th>',{
					'class':'varname',
					'html':$('<span>',{
					    'html':$(variable).attr('code')})
				    })
				}));
				
				$(variable).find('value').each(function(i, value){
				    $('#var_'+nbvar).append($('<td>',{
					'class':'varval',
					'html':$('<span>',{
					    'html':$(value).find('content').html()
					})
				    }))
				});
			    });
			    $('.critname').each(function(i,e) {
				ui_crit_name($(e));
			    });
			    $('.critval').each(function(i,e) {
				ui_crit_val($(e));
			    });
			    $('.varname').each(function(i,e) {
				ui_var_name($(e));
			    });
			    check();
			    disable_save();
			});
		})
	})

    // ajout des actions en-tetes de colonne
    var ui_col_header = function() {
	return $('<span>', {
	    'class':'pull-right btn-group',
	    'html':[
		$('<button>',{
		    'class':'btn btn-default btn-xs var_col_copy',
		    'type':'button',
		    'title':'Dupliquer la colonne', 
		    'html': $('<i>',{
			'class':"fa fa-copy"
		    })
		}),
		$('<button>',{
		    'class':'btn btn-default btn-xs var_col_delete',
		    'type':'button',
		    'title':'Supprimer la colonne', 
		    'html': $('<i>',{
			'class':"fa fa-trash-o"
		    })
		})
	    ]
	})
    }

    $('#main').on('click', '.var_col_copy', function(){
	var colnum = $(this).closest('td').prevAll('td').length;
	$('#main tr').each(function(i,e) {
	    var cell = $($(e).children()[colnum])
	    cell.after(cell.clone())
	})
	check();
    })
    
    $('#main').on('click', '.var_col_delete', function(){
	var colnum = $(this).closest('td').prevAll('td').length;
	$('#main tr').each(function(i,e) {
	    $($(e).children()[colnum]).remove()
	})
    	check();
    })

    // ajout des actions d'une cellule critère name
    
    var ui_crit_name = function(cell) {
	cell.append($('<span>', {
	    'class':'pull-right',
	    'html':$('<button>',{
		'class':'btn btn-default btn-xs btn-remove-critname',
		'title':'Supprimer le critère',
		'html': $('<i>',{
		    'class':"fa fa-trash-o"
		})
	    })
	}))
    }

    $('#main').on('click', '.btn-remove-critname', function(){
	enable_add_crit($(this).closest('tr').data('crit'));
	$(this).closest('tr').remove();
	check();
    })
    
    // ajout des actions d'une cellule critère value

    var ui_crit_val = function(cell) {
	var critname = cell.data('crit');
	var critval = cell.find('span').first().html();
	cell.append($('<span>', {
	    'class':'pull-right btn-group',
	    'html':[
		$('<button>',{
		    'class':'btn btn-default btn-xs dropdown-toggle',
		    'type':'button',
		    'data-toggle':'dropdown',
		    'html': $('<span>',{
			'class':"caret"
		    })
		}),
		$('<ul>',{
		    'class':"dropdown-menu",
		    'role':"menu",		  
		    'html':$.map(criteria[critname], function(e) {
			if (e != critval)
			return $('<li>',{
			    'html':$('<a>',{
				'class':'crit_val_change',
				'html':e
			    })
			})
		    })
		})
	    ]
	}))
    }
    
    $('#main').on('click', '.crit_val_change', function(){
	var val = $(this).html()
	var cell = $(this).closest('th') 
	cell.find('span').first().html(val);
	cell.find('span.btn-group').first().remove();
	ui_crit_val(cell);
	check();
    });

    // ajout des actions d'une cellule variable name
    
    var ui_var_name = function(cell) {
	cell.append([
	    $('<span>', {
		'class':'pull-right btn-group',
		'html':[
		    $('<button>',{
			'class':'btn btn-default btn-xs var_name_copy',
			'type':'button',
			'title':'Dupliquer la colonne', 
			'html': $('<i>',{
			    'class':"fa fa-copy"
			})
		    }),

		    $('<button>',{
			'class':'btn btn-default btn-xs var_name_edit',
			'type':'button',
			'title':'Modifier les valeurs', 
			'html': $('<i>',{
			    'class':"fa fa-pencil-square-o"
			})
		    }),
		    $('<button>',{
			'class':'btn btn-default btn-xs var_name_delete',
			'type':'button',
			'title':'Supprimer la variable', 
			'html': $('<i>',{
			    'class':"fa fa-trash-o"
			})
		    })
		]
	    })
	])	    
    };
    
    $('#main').on('click', '.var_name_copy', function(){
	var row = $(this).closest('tr').html();
	nbvar++;
	$(this).closest('tr').after($('<tr>',{
	    'id':'var_'+nbvar,
	    'html':$(row)
	}));
	check();
    });

    $('#main').on('click', '.var_name_delete', function(){
	$(this).closest('tr').remove(); 
	check();
    });

    var var_edit =  function(){
	$(this).closest('tr').find('th').each(function(i,e) {
	    $(e).children('span').hide()
	    var value = $(e).children('span').first().html();
	    $(e).append($('<input>', {
		'type':"text",
		'value':value
	    }));
	    $(e).append($('<span>', {
		'class':'pull-right var_edit_confirm_span',
		'html':$('<button>', {
		    'type':"button",
		    'title':'Valider', 
		    'class':"btn btn-xs btn-primary var_edit_confirm",
		    'html':$('<i>',{'class':"fa fa-check"})
		})
	    }));
	    
	});
	$(this).closest('tr').find('td').each(function(i,e) {
	    $(e).children('span').hide()
	    var value = $(e).children('span').first().html();
	    $(e).append($('<input>', {
		'type':"text",
		'value':value
	    }));
	});
	disable_commands();
    };
    
    
    $('#main').on('click', '.var_name_edit', var_edit);

    $('#main').on('click', '.var_edit_confirm', function(){
	var tr = $(this).closest('tr');
	tr.find('th').each(function(i,e) {
	    var value = $(e).children('input').get()[0].value
	    $(e).children('span').last().remove();
	    $(e).children('input').remove();
	    $(e).children('span').first().html(value);
	    $(e).children('span').show()
	    
	});
	tr.find('td').each(function(i,e) {
	    var value = $(e).children('input').get()[0].value
	    $(e).children('input').remove();
	    $(e).children('span').first().html(value);
	    $(e).children('span').show()
	});
	enable_commands();
	check();
    });

    
    
    // actions des boutons latéraux
    
    var add_variable = function() {
	nbvar++;
    	$('#main tbody').prepend($('<tr>',{
	    'id':'var_'+nbvar,
	    'html':$('<th>',{
		'class':'varname',
		'html':$('<span>',{
		    'html':""})
	    })
	}));
    
	$('#main thead').find('tr.info').first().find('th').each(function(i, r){
	    if(i > 0) {
		$('#var_'+nbvar).append($('<td>',{
		    'class':'varval',
		    'html':$('<span>',{
			'html':""
		    })
		}))
	    }
	});
	var cell = $('#var_'+nbvar+" th").first()
	ui_var_name(cell);
	cell.each(var_edit);
	
    }
							   

    $('#btn_add_var').click(add_variable);
    
    $('#btn_add_col').click(function() {
	$('#main thead').find('tr.colheaders').first().append(
	    $('<td>', {
		'class':'colheader',
		'html':ui_col_header()
	    })
	);
	$('#main thead').find('tr.info').each(function() {
	    var critname = $(this).find('th').first().find("span").first().html(); 
	    var cell=$('<th>',{
		'class':'critval',
		'data-crit':critname,
		'html':$('<span>',{
		    'html':"--"})
	    });
	    $(this).append(cell);
	    ui_crit_val(cell);
	})
	$('#main tbody').find('tr').each(function() {
	    var cell=$('<td>',{
		'class':'varval',
		'html':$('<span>',{
		    'html':"--"
		})
	    });
	    $(this).append(cell);
	})
	check();
    });

    $('body').on('click', '.item_add_crit', function() {
	var critname = $(this).data('crit');
	var cell = $('<th>',{
	    'class':'critname',
	    'html':$('<span>',{
		'html':critname
	    })
	});
	
	$('#main thead').append($('<tr>',{
	    'id':'crit_'+critname,
	    'data-crit':critname,
	    'class':'info',
	    'html':cell
	}));
	ui_crit_name(cell);
	
	$('#main tbody tr').first().find('td').each(function() {
	    cell = $('<th>',{
		'class':'critval',
		'data-crit':critname,
		'html':$('<span>',{
		    'html':'--'
		})
	    })
	    $('#main thead tr').last().append(cell);
	    ui_crit_val(cell);
	});
	disable_add_crit(critname);
	check();
    });

    var disable_add_crit = function(critname) {
	$('.item_add_crit_'+critname).parent().addClass('disabled')
    }
    
    var enable_add_crit = function(critname) {
	$('.item_add_crit_'+critname).parent().removeClass('disabled')
    }
    
    var disable_commands = function() {
	$('.btn-remove-critname').addClass('disabled')
	$('.var_name_delete').addClass('disabled')
	$('.var_name_edit').addClass('disabled')
	$('.critval button').addClass('disabled')
	$('.sidebtns button').addClass('disabled')
    }
    
    var enable_commands = function() {
	$('.btn-remove-critname').removeClass('disabled')
	$('.var_name_delete').removeClass('disabled')
	$('.var_name_edit').removeClass('disabled')
	$('.critval button').removeClass('disabled')
	$('.sidebtns button').removeClass('disabled')
    }
    
    // check variable coherence
    var check = function() {
	var res = true;
	var critvals = $('#main th.critval')
	critvals.each(function(i,cell) {
	    var critname = $(cell).data('crit');
	    var critval = $(cell).find('span').first().html();

	    if ($.inArray(critval,criteria[critname]) == -1) {
		$(cell).addClass('danger')
		$(cell).attr('title','La valeur n\'est pas valide pour ce critère');
		res = false
	    } else {
		$(cell).removeClass('danger')
		$(cell).removeAttr('title');
	    }
	});
	if (res)
	    enable_save()
	else
	    disable_save()
	return res
    }
})

