$(document).ready(function() {
/*
    $('a[data-section]').on('click', function(ev) {
	var content = $("ul[data-section-content='"+$(this).attr("data-section")+"']"); 
	var icon = $(this).find('i'); 
	content.toggleClass('hidden');
	if (content.hasClass('hidden'))
	{
	    icon.attr('class','glyphicon glyphicon-folder-close');
	} else {
	    icon.attr('class','glyphicon glyphicon-folder-open');
	}  
	ev.preventDefault();
	ev.stopPropagation();
    })
    $('#ksearchinput').on('keyup', function() {
	search();
    });

    $('#search_btn').on('click', function() {
	search();
 	highlight();
   });

    $('#searchclose').on('click', function() {
	$('#search_results').hide();
 	unhighlight();
   });
  */  

/*
<div id="os" class="well navbar-nav col-md-12 col-sm-12">
            <h5 class="col-md-12 col-sm-3">Système d'exploitation</h5>
              <ul class="col-md-12 col-sm-9 list-group list-unstyled">
                
                  <li class="list-group-item text-center col-md-4 col-sm-4 col-lg-4 col-xs-4">
                    <a href="index.html">
                      Windows
                    </a>
                  </li>
                  <li class="list-group-item text-center col-md-4 col-sm-4 col-lg-4 col-xs-4">
                    <a href="index.html">
                      Windows
                    </a>
                  </li>
                  <li class="list-group-item text-center col-md-4 col-sm-4 col-lg-4 col-xs-4">
                    <a href="index.html">
                      Windows
                    </a>
                  </li>                
              </ul>

              
            </div>
*/

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
       build_ui_menus(conditions);
   }
    
    var build_ui_buttons = function(conditions) {
	$.each(conditions, function(i,c) {
	    $('<div>',
	      { "class":"well navbar-nav col-md-12 col-sm-12 user-condition",
		"id":"uc_"+i,
		"html":[$('<div>', {
		    "class":"col-md-12 col-sm-3",
		    "html":i}),
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
		    "class":"col-md-12 col-sm-3",
		    "html":[
			$('<div>',{
			    "class":"col-md-8 col-sm-12",
			    "html":i
			}),
			$('<div>', {
			    "class":"btn-group col-md-4 col-sm-12",
			    "html":[
				$("<button>", {
				    "type":"button",
				    "class":"btn btn-default btn-xs dropdown-toggle",
				    "data-toggle":"dropdown",
				    "html":[c[0]+" ",$("<span>", {"class":"caret"})]
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
			    "html":v
			}).click(function() {
			    $('#uc_'+i).data('codevalue',$(this).data('code'));
			    $('#uc_'+i+" button").html(v+" <span class='caret'/>");
			    filter_view();
			})
		}).appendTo($('#uc_' + i + " ul"));
	    });
	});
	
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
