$(document).ready(function() {

   var build_ui = function() {
       var crit, val;
       var conditions = {}
       $.get('/criteria').success(function(xml_criteria) {
//	   var xml_criteria = $($.parseXML(data))
	   $(xml_criteria).find('criterion[type=enum]').each(function(i,c){
	       var crit = $(c).attr('code');
	       conditions[crit] = [];
	       $(c).children('value').each(function(j,v){
		   conditions[crit].push($(v).text());
	       });
	   });
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
	    if (value != '*')
		conditions[cond]=value;
	});
	
	
	$(".topiccontent").find("*[class*='=']").each(function(e) {
	    cl = this.className.replace(/ /g,'');
	    if (check_condition(cl, conditions))
                this.style.display = "block";
	    else
                this.style.display = "none";
	});
    }

    check_condition = function(expr, crit) {
	var cond = expr.split('=');
	var c = cond[0];

	var expr = expr.substr(cond[0].length+1, expr.length);

	var r1 = !(expr.search(/,/) < 0);
	var r2 = !(expr.search(/;/) < 0);
	var r3 = !(expr.search(/\\/) < 0);
	
	// if criteria not selected
	if(!crit[c] && !r1) {
            return true;
	} else if(!crit[c]) {
            if(cond.length > 2) {
		//NoticePapier,NoticeWeb, ZONE = WestEurope, EastEurope
		var ncond = cond[1].split(',').pop();
		if(ncond.search(/;/) < 0)
                    return check_condition(expr.substr(cond[1].length-ncond.length, expr.length), crit);
		else
                    return false;
            } else {
		return true;
            }
	}
	
	// SIMPLE condition
	if(!r1 && !r2 && !r3) {
            return crit[c] == cond[1];
	}
	// EXCLUDE condition
	else if(!r1 && !r2 && r3) {
            return check_condition_exclude(expr, crit, c, cond[1]).result;
	}
	// AND condition
	else if(!r1 && r2 && !r3) {
            return check_condition_and(expr, crit, c);
	}
	// AND + EXCLUDE conditions
	else if(!r1 && r2 && r3) {
            var pos1 = expr.search(/;/);
            var pos2 = expr.search(/\\/);
            if(pos1 < pos2) {
		return check_condition_and(expr, crit, c) && check_condition(expr.substr(pos2+1, expr.length), crit);
            } else {
		var exclu = check_condition_exclude(expr, crit, c, cond[1]);
		return exclu.result && check_condition(expr.substr(exclu.pos+1, expr.length), crit);
            }
	}
	// OR condition
	else if(r1 && !r2 && !r3) {
            return check_condition_or(expr, crit, c).result;
	} 
	// OR + EXCLUDE conditions
	else if(r1 && !r2 && r3) {
            var pos1 = expr.search(/,/);
            var pos2 = expr.search(/\\/);
            if(pos1 < pos2) {
		var cor = check_condition_or(expr, crit, c)
		return cor.result || check_condition(expr.substr(cor.pos, expr.length), crit);
            } else {
		var exclu = check_condition_exclude(expr, crit, c, cond[1]);
		return exclu.result || check_condition(expr.substr(exclu.pos+1, expr.length), crit);
            }
	}
	// OR + AND conditions
	else if(r1 && r2 && !r3) {
            var pos1 = expr.search(/,/);
            var pos2 = expr.search(/;/);
            if(pos1 < pos2)
		return check_condition_or(expr, crit, c) && check_condition(expr.substr(pos2+1, expr.length), crit);
            else
		return check_condition_and(expr, crit, c) && check_condition(expr.substr(pos1+1, expr.length), crit);
	} 
	// OR + AND + EXCLUDE conditions
	else if(r1 && r2 && r3) {
            var pos1 = expr.search(/,/);
            var pos2 = expr.search(/;/);
            var pos3 = expr.search(/\\/);
            if(pos1 < pos2 && pos1 < pos3) {
		if(pos2 < pos3)
                    return check_condition_or(expr, crit, c) || check_condition(expr.substr(pos2+1, expr.length), crit);
		else
                    return check_condition_or(expr, crit, c).result || check_condition(expr.substr(pos3+1, expr.length), crit);
            } else if(pos2 < pos1 && pos2 < pos3) {
		if(pos1 < pos3)
                    return check_condition_and(expr, crit, c) && check_condition(expr.substr(pos1+1, expr.length), crit);
		else
                    return check_condition_and(expr, crit, c) && check_condition(expr.substr(pos3+1, expr.length), crit);
            } else {
		var exclu = check_condition_exclude(expr, crit, c, cond[1]);
		return exclu.result && check_condition(expr.substr(exclu.pos+1, expr.length), crit);
            }
	}
	return false;
    }


    // Check EXCLUDE condition
    var check_condition_exclude = function(expr, crit, cond, val) {
	var curpos = 0;
	var pos = expr.search(/\\/);
	
	var splitVal = val.substr(pos+1,val.length).split(",");
	if (!(expr.search(new RegExp(splitVal[splitVal.length-1]+"=")) < 0))
            splitVal.pop();
	
	for(var i=0; i<splitVal.length; i++) {
            if(crit[cond] == splitVal[i])
		return {'result': false, 'pos': 0};
            curpos += splitVal[i].length+1;
	}
	return {'result': true, 'pos': curpos};
    }

    // Check OR condition
    var check_condition_or = function(expr, crit, cond) {
	var curval;
	var val = expr.split(/[a-zA-Z0-9]+=/)[0].split(',');
	var curpos = 0;
	for(i=0; i<val.length; i++) {
            curval = val[i];
            if(curval != "") {
		curval = curval.split(';')[0];
		if(crit[cond] == curval)
                    return {'result': true, 'pos': 0};
		curpos+= curval.length+1;
            }
	}
	return {'result': false, 'pos': curpos};
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