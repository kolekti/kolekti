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
		"html":[$('<h5>', {
		    "class":"col-md-12 col-sm-3",
		   "html":i}),
			$('<div>', {
			    "class":"btn-group btn-group-justified",
			    "data-toggle":"buttons"
			})
		       ]
	      }).appendTo($('#userconditions'));
	    
      	    $.each(c,function(j,v){
		console.log(c,v);
		$('<label>', {
		    "class":"btn btn-default",
		    html:[$('<input>', {
			type:"radio",
			id:"uc_"+i+"_"+v,
		       name:"uc_"+i
		    }),v]
		    
		}).appendTo($('#uc_'+i+" .btn-group"));
	    });
	});

    var build_ui_menus = function(conditions) {
	$.each(conditions, function(i,c) {
	    $('<div>',
	      { "class":"well navbar-nav col-md-12 col-sm-12 user-condition",
		"id":"uc_"+i,
		"html":[$('<h5>', {
		    "class":"col-md-12 col-sm-3",
		   "html":i}),
			$('<div>', {
			    "class":"btn-group btn-group-justified",
			    "data-toggle":"buttons"
			})
		       ]
	      }).appendTo($('#userconditions'));
	    
      	    $.each(c,function(j,v){
		console.log(c,v);
		$('<label>', {
		    "class":"btn btn-default",
		    html:[$('<input>', {
			type:"radio",
			id:"uc_"+i+"_"+v,
		       name:"uc_"+i
		    }),v]
		    
		}).appendTo($('#uc_'+i+" .btn-group"));
	    });
	});
	
    }
		   
    build_ui();
 /*
    var search = function() {
	var words = $("#ksearchinput").val();
	if (words.length > 2) {
	    a_search(words);
	    $("#search_results").show();
	} else {
	    $("#search_results").hide();
 	    unhighlight();
	}
    }

    $('#indexinner').each(function(e) {
	var row = $(this);
	var pos = 0;
	$(this).find('.span3').each(function() {
	    if (pos == 3) {
		pos = 0;
		newrow = $('<div class="row-fluid">');
		row.after(newrow);
		row = newrow;
	    }
	    row.append($(this));
	    pos ++;
	});
    });
   */ 
 })