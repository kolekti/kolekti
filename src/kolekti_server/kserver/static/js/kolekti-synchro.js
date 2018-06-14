
$(document).ready(function() {

    var populate_tree = function(root, statuses) {
        if (!root.length)
            return
        var dirlist = $('<ul>')
        root.append(dirlist)
        $.each(statuses, function(name, value) {
            if (name == "__self")
               return;
            item = $('<li>')
            dirlist.append(item)
            var toggle  = $('<span class="toggle"><i class="glyphicon glyphicon-chevron-right open"></i><i class="glyphicon glyphicon-chevron-down close"></i></span>')
            item.append(toggle)
            var checkbox = $('<input type="checkbox" class="sync_check"/>')
            checkbox.addClass('sync_check_'+value.__self.kolekti_status)
            item.append(checkbox)
            var name = $('<span class="sync_name">'+name+'</span>')
            item.append(name)
            item.attr('title', value.__self.path)
            item.attr('data-status', value.__self.kolekti_status)
            item.attr('data-kind', value.__self.kind)
            populate_tree(item, value)
        })
        
    }

    var znodes = function(statuses, status) {
        var nodes = []
        $.each(statuses, function(name, value) {
            if (name == "__self")
                return;
            var node_status = value.__self.kolekti_status
            var node_inherited_status = value.__self.kolekti_inherited_status
            var node_detail_status =
                "L" + value.__self.kolekti_details_status
            var children = znodes(value, status)
            
            var node = {"name":name,
                        "open":(node_inherited_status == status)?true:false,
                        "checked":(node_inherited_status == status)?true:false,
                        "chkDisabled":(node_inherited_status == status)?false:true,
                        "status":node_status,
                        "hstatus":node_inherited_status
                        "dstatus":node_deatil_status,
                       }
            if (children.length)
                node.children = children
            nodes.push(node)
        });
        return nodes;
    }
    
    var setup_tree = function(root, status) {
        root.find('li').each(function() {
            if ($(this).data('status') != status) {
                $(this).addClass('sync_node_disabled')
                $(this).find('input.sync_check')
                  .attr('disabled','yes')
                $(this).children('.toggle').find('.open')
                  .addClass('sync-hidden')
            } else {
                $(this).children('.toggle').find('.close')
                  .addClass('sync-hidden')
                $(this).children('input.sync_check')
                  .attr('checked','yes')
                
            }
        })
    }

    $.get('/sync/tree')
        .done(function(data) {
            console.log('data loaded')
            console.log(data)
            main_status = $.map(data, function(dir) {
                return dir.__self.kolekti_inherited_status
            })
            var status;
            if ($.inArray('conflict', main_status)) {
                status = "conflict";
                $('.sync_conflict').removeClass('sync_hidden')
            }
            else if ($.inArray('merge' , main_status)) {
                status = "merge"
                $('.sync_merge').removeClass('sync_hidden')
            }
            else if ($.inArray('commit', main_status)) {
                status = "commit"
                $('.sync_commit').removeClass('sync_hidden')
            }
            else if ($.inArray('update', main_status)) {
                status = "update"
                $('.sync_update').removeClass('sync_hidden')
            }
            else {
                status = "ok"
                $('.sync_ok').removeClass('sync_hidden')
            }
            $('.sync_loading').addClass('sync_hidden')

            
            var myOnExpand = function(event, treeId, treeNode) {
                console.log('expand')
                console.log(treeNode)
                
            };
            
            var myOnClick = function(event, treeId, treeNode) {
                console.log('click')
                console.log(treeNode)
                
            };
            var myOnNodeCreated = function(event, treeId, treeNode) {
                $('#'  + treeNode.tId+ '_span').addClass('status-' + treeNode.status)
                $('#'  + treeNode.tId+ '_span').addClass('hstatus-' + treeNode.hstatus)
                
            };
            
            var setting = {
                check: {
                    enable: true,
                    chkStyle: "checkbox",
                    chkboxType: { "Y": "s", "N": "s" }
                },
                callback: {
                    onExpand: myOnExpand,
                    onClick: myOnClick,
                    onNodeCreated:myOnNodeCreated
                }

            };

            
            var tree = $('.sync_' + status +' .sync_tree')
            tree.addClass('active')
            zTreeObj = $.fn.zTree.init(tree, setting, znodes(data, status));
        })

    
    $('#selectall').change(function() {
	    $('.selectentry').prop('checked',$(this).prop('checked'))
	check_action()
    });
    
    var check_action = function(e) {
	if ($('.selectentry').length) {
	    var map = $('.selectentry').filter(function() { return $(this).prop('checked')})
	    if(map.length == 0) 
		$('.btn-action-synchro').addClass('disabled')
	    else
		$('.btn-action-synchro').removeClass('disabled')
	}
    };
		  
    $('body').on('change','.selectentry',check_action);
    check_action()

		  
    $('body').on('change','select',function(e) {
	var val = $(this).val();
	if (val == "local" || val == "merge" || val == "commit") {
	    $("#commitmsg").show();
	} else {
	    $("#commitmsg").hide();
	}
    });
    
    $('form').on('submit', function() {
	console.log("submit form");
	$('#modal_processing').modal('show')
    })
		  
    /*		 
    $('body').on('click','.btn-select-merge',function(e) {
	action = $('.select-merge').val();
	console.log(action);
	$('.entry-merge:selected').each(function(i,e) {
	    $.post('/sync/merge/'+action, {
		'path':$(this).data('path')
	    })
		.done(function(data) {
		    $('.modal-body').append($(data))
		});
	    $('.modal-title').html('Synchronisation')		
	    $('.modal-footer').html(
		$('<button>',{
		    "class":"btn btn-default", 
		    "html":"fermer"})
		    .on('click',function() { window.location.reload()})
		)
	    $('.modal').modal();
	});
    });

    $('body').on('click','.btn-select-conflit',function(e) {
	action = $('.select-confilt').val();
	console.log(action);
	$('.entry-conflit:selected').each(function(i,e) {
	    $.post('/sync/conflit/'+action, {
		'path':$(this).data('path')
	    })
		.done(function(data) {
		    $('.modal-body').append($(data))
		});
	    $('.modal-title').html('Synchronisation')		
	    $  ('.modal-footer').html(
		$('<button>',{
		    "class":"btn btn-default", 
		    "html":"fermer"})
		    .on('click',function() { window.location.reload()})
		)
	    $('.modal').modal();
	});
    });
*/
    $('#syncromsg').focus()    
})



/*


            {% with node=changes %}
            {%include "synchro/tree_view_template.html" %}
            {% endwith %}
            
            {% comment %}
		    {% if changes.error|length %}
		    {% for e in changes.error %}
		    <div class="checkbox">
		      <label>
		        <input class="selectentry entry-conflict" data-path="{{ e.path }}" data-basename="{{ e.basename }}" type="checkbox" value="{{e.path}}" name="fileselect" />
		        {{ e.path }}
		      </label>
		      <br>
		    </div>
		    {% endfor %}
		    {% else %}
		    {% for e in changes.conflict %}
		    <div class="checkbox">
		      <label>
		        <input class="selectentry entrey-conflit" data-path="{{ e.path }}" type="checkbox" value="{{e.path}}" name="fileselect" />
		        {{ e.path }} 
		      </label>
		      <br>
		    </div>
		    {% endfor %}
		    {% endif %}
            {% endcomment %}




-----------------------



		      {% for e in changes.merge %}
		      <div class="checkbox">
		        <label>
		          <input class="selectentry entry-merge" data-path="{{ e.path }}" type="checkbox" value="{{e.path}}" name="fileselect" checked="checked"/>
		          {{ e.path }} 
		        </label>
		        <br>
		      </div>
		      {% endfor %}


-------------------------

	     <ul>
	       
	       {% for e in changes.update %}
	       <li>{{ e.path }}
		     {% comment %}
		     {% if e.kind == "file" %}<span class="pull-right"><a title="[R:{{e.rstatus}} W:{{e.wstatus}}]" href="/sync/diff?file={{e.path}}" target="diff">diff</a></span>{% endif %}		   {% endcomment %}
	       </li>
	       {% endfor %}
	     </ul>


---------------------------


            
		    {% for e in changes.commit %}
	       	<div class="checkbox">
		      <label title="{{e.wstatus}}">
		        <input class="selectentry entry-commit" data-path="{{ e.path }}" type="checkbox" value="{{e.path}}" name="fileselect" />
		        {% if e.wstatus == 'deleted' %}
		        <s>{{ e.path }}</s>
		        {% else %}
		        {{ e.path }}
		        {% endif %}
		        {% if e.wstatus == 'added' %} (ajout){% endif %}
		      </label>

		      {% comment %}
		      {% if e.kind == "file" %}<span class="pull-right"><a title="[R:{{e.rstatus}} W:{{e.wstatus}}]" href="/sync/diff?file={{e.path}}" target="diff">diff</a></span>{% endif %}
		      {% endcomment %}
              
		    </div>
		    {% endfor %}


*/
