$(document).ready(function() {
    var conditions_labels = {}
    var build_ui = function() {
        var crit, val;
        var conditions = {}
        
        $('meta[scheme=user_condition]').each(
	        function(i,m) {
	            crit = $(m).attr('name');
	            val = $(m).attr('content');
	            if (conditions[crit] == undefined)
		            conditions[crit] = [];
	            conditions[crit].push(val); 
	        });
        
        $('meta[scheme=user_condition_label]').each(
	        function(i,m) {
	            code = $(m).attr('name');
	            label = $(m).attr('content');
	            conditions_labels[code] = label; 
	        });
        build_ui_menus(conditions);
    }

    var build_ui_buttons = function(conditions) {
	    $.each(conditions, function(i,c) {
	        $('<div>',
	          { "class":"well navbar-nav col-md-12 col-sm-12 user-condition",
		        "id":"uc_"+i,
		        "html":[$('<div>', {
		            "class":"foo",
		            "html":get_label(i)}),
			            $('<div>', {
			                "class":"btn-group btn-group-justified",
			                "data-toggle":"buttons"
			                
			            })
		               ]
	          }).appendTo($('#userconditions'));
	        
      	    $.each(c,function(j,v){
		        $('<label>', {
		            "class":"btn btn-default",
		            html:[$('<input>', {
			            type:"radio",
			            "class":"userselect",
			            id:"uc_"+i+"_"+v,
		                name:"uc_"+i
		            }).change(function() {
			            console.log('click');
			            filter_view();
		            }),v]
		            
		        }).appendTo($('#uc_'+i+" .btn-group"));
	        });
	    });
    }
    
    var build_ui_menus = function(conditions) {
	    $.each(conditions, function(i,c) {
	        $('<div>',
	          { "class":"col-md-12 col-sm-12 user-condition",
		        "id":"uc_"+i,
		        "data-code":i,
		        "data-codevalue":c[0],
		        "html":[$('<div>', {
		            "class":"user-condition-group",
		            "html":[
			            $('<div>',{
			                "class":"col-md-12 col-sm-3",
			                "html":get_label(i)
			            }),
			            $('<div>', {
			                "class":"btn-group col-md-12 col-sm-12",
			                "html":[
				                $("<button>", {
				                    "type":"button",
				                    "class":"btn btn-default btn-xs dropdown-toggle",
				                    "data-toggle":"dropdown",
				                    "html":[get_label(c[0])+" ",$("<span>", {"class":"caret"})]
				                }),
				                $('<ul>',{
				                    "class":"dropdown-menu",
				                    "role":'menu' 
				                })]
			            })
		            ]
		        })]
	          }).appendTo($('#userconditions'));
	        
      	    $.each(c,function(j,v){
		        $('<li>', {
		            html:
			        $('<a>', {
			            "href":"#",
			            "id":"uc_"+i+"_"+v,
			            "data-code":v,
			            "html":get_label(v)
			        }).click(function() {
			            $('#uc_'+i).data('codevalue',$(this).data('code'));
			            $('#uc_'+i+" button").html(v+" <span class='caret'/>");
			            filter_view();
			        })
		        }).appendTo($('#uc_' + i + " ul"));
	        });
	    });
	    
    }

    get_label = function(code) {
        return conditions_labels[code];
    }
    
    // Filter view with selected criterias
    
    filter_view = function(arg) {
	    var s, value, cl;
	    var me = this;
	    var conditions = new Array();
        
	    $(".user-condition").each(function(i,input) {
	        var cond = $(this).data('code');
	        var value = $(this).data('codevalue');
	        conditions[cond]=value;
	    });
	    
	    
	    $("#k-topic").find("*[class*='=']").each(function(e) {
	        cl = this.className.replace(/ /g,'');
	        if (eval_condition_expression(cl, conditions))
                this.style.display = "block";
	        else
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
    
	
		   
    build_ui();
    filter_view();	
})
