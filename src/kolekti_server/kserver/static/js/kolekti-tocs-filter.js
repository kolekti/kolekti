$(document).ready(function() {

   var build_ui = function() {
       var crit, val;
       var conditions = {}
       $.get('/criteria.json').success(
	   function(conditions) {
//	   var xml_criteria = $($.parseXML(data))
/*	   $(xml_criteria).find('criterion[type=enum]').each(function(i,c){
	       var crit = $(c).attr('code');
	       conditions[crit] = [];
	       $(c).children('value').each(function(j,v){
		   conditions[crit].push($(v).text());
	       });
	   });
*/
	   build_ui_menus(conditions);
       })
   }

    var build_ui_menus = function(conditions) {
	$.each(conditions, function(i,c) {
	    $('<li>',
	      { "class":"list-group-item user-condition",
		"id":"uc_"+i,
		"data-code":i,
		"data-codevalue":"*",
		"html":[i,
			$('<span>', {
			    "class":"pull-right",
			    "html":[
				$("<button>", {
				    "type":"button",
				    "class":"btn btn-xs btn-default dropdown-toggle",
				    "data-toggle":"dropdown",
				    "html":["Non filtré ",$("<span>", {"class":"caret"})]
				}),
				$('<ul>',{
				    "class":"dropdown-menu",
				    "role":'menu' 
				})]
			})
		    ]
	      }).appendTo($('#userconditions'));

	    $('<li>', {
		html:
		$('<a>', {
		    "href":"#",
		    "id":"uc_"+i+"_*",
		    "data-code":'*',
		    "html":"Non filtré"
		}).click(function() {
		    $('#uc_'+i).data('codevalue',$(this).data('code'));
		    $('#uc_'+i+" button").html("Non filtré <span class='caret'/>");
		    filter_view();
		})
	    }).appendTo($('#uc_' + i + " ul"));
	    
	    $.each(c,function(j,v){
		$('<li>', {
		    html:
			$('<a>', {
			    "href":"#",
			    "id":"uc_"+i+"_"+v,
			    "data-code":v,
			    "html":v
			}).click(function(e) {
			    e.preventDefault();
			    $('#uc_'+i).data('codevalue',$(this).data('code'));
			    $('#uc_'+i+" button").html(v+" <span class='caret'/>");
			    filter_view();
			})
		}).appendTo($('#uc_' + i + " ul"));
	    });
	});
	
    }
    
    // Filter view with selected criterias
    
    var filter_view = function(arg) {
	var s, value, cl;
	var me = this;
	var conditions = new Array();
	$(".user-condition").each(function(i,input) {
	    var cond = $(this).data('code');
	    var value = $(this).data('codevalue');
	    if (value != '*')
		conditions[cond]=value;
	});
	
	
	$(".topiccontent").find("*[class*='=']").each(function(e) {
	    cl = this.className.replace(/ /g,'');
	    this.style.display = "block";
	    if (!eval_condition_expression(cl, conditions))
                this.style.display = "none";
	});
    }

    var eval_condition_expression = function(expr, selected_values) {
	var cond = expr.split(';');
	var c = cond[0];
	
	for (var ic=0; ic < cond.length; ic++) {
	    if (eval_condition_list(cond[ic], selected_values))
		continue;
	    return false;
	}  
	return true;
    }

    var eval_condition_list = function(expr, selected_values) {
	var crit_vals = expr.split('=');
	var crit = crit_vals[0];
	var vals = crit_vals[1];
	if (!selected_values[crit]) return true;
	if (vals[0] == '\\') return ! value_in_list(selected_values[crit], vals.substr(1));
	return value_in_list(selected_values[crit], vals);
    } 

    var value_in_list = function(value, list) {
	items = list.split(',');
	return items.indexOf(value) != -1
    }


    $("#btn_toggle_conditions").on('click', function() {
	if(! $(this).hasClass('active')) {
	    $('.main *[class*="="]').each(function(i,e){
		$(e).wrap("<div class='panel panel-default'><div class='panel-body uicond'></div></div>");
		$(e).closest(".panel").prepend($("<div class='panel-heading uicond'>" + $(e).attr("class") + "</div>"));
		$(e).addClass('uicond');
	    });
	} else {
	    $('.panel-heading.uicond').remove();
	    $('.uicond').unwrap();
	    $('.uicond').removeClass('uicond');
	}
    })
    
    build_ui();
    filter_view();
	
})