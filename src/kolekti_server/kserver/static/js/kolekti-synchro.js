var translations = {
    'dir' : 'dossier',
    'file': 'fichier'
}

$(document).ready(function() {
    
    var myOnExpand = function(event, treeId, treeNode) {
        console.log('expand')
        console.log(treeNode)
        
    };
            
    var myOnCheck = function(event, treeId, treeNode) {
        console.log('check')
        console.log(treeNode)        
        console.log(event)        
        check_action()
    };
            
    var myOnClick = function(event, treeId, treeNode) {
        console.log('click')
        console.log(treeNode)
        if (treeNode.status == treestatus) {
            $('#syncdetails .sync-det-type').html(translations[treeNode.ktype])
            $('#syncdetails .sync-det-name').html(treeNode.name)
            $('#syncdetails .sync-det-wstatus').html(treeNode.kwstatus)
            $('#syncdetails .sync-det-rstatus').html(treeNode.krstatus)
            $('#syncdetails').show()
        } else {
            $('#syncdetails').hide()
        }
    };
    var myOnNodeCreated = function(event, treeId, treeNode) {
        $('#'  + treeNode.tId+ '_span').addClass('status-' + treeNode.status)
        $('#'  + treeNode.tId+ '_span').addClass('hstatus-' + treeNode.hstatus)
        var treestatus = $('#'  + treeNode.tId+ '_span').closest('.ztree').data('status')
        if (treeNode.hstatus != treestatus && treeNode.status != treestatus)
            $('#'  + treeNode.tId+ '_span').closest('li').addClass('listitem-hiddable')
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
            onNodeCreated:myOnNodeCreated,
            onCheck:myOnCheck
            
        }
    };

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
                        "kpath":value.__self.path,
                        "ktype":value.__self.kind,
                        "krstatus":value.__self.rstatus,
                        "kwstatus":value.__self.wstatus,
                        "open":(node_inherited_status == status)?true:false,
                        "checked":(node_status == status)?true:false,
                        "chkDisabled":(node_status == status)?false:true,
                        "status":node_status,
                        "hstatus":node_inherited_status,
                        "dstatus":node_detail_status,
                       }
            if (children.length)
                node.children = children
            nodes.push(node)
        });
        return nodes;
    }
    
    $('#syncdetails').hide()
    $('#sync_error').hide()
    var treedata;
    var treestatus;
    
    $.get(Urls.kolekti_sync_tree(kolekti.project))
        .done(function(data) {
            treedata = data
            console.log('data loaded')
            main_status = $.map(data, function(dir, x) {
                if (x != '__self')
                    return dir.__self.kolekti_inherited_status
            })
            console.log(main_status)
            
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
            $('#sync_loading').addClass('sync_hidden')
            treestatus = status;
            
            var tree = $('.sync_' + status +' .sync_tree')
            tree.addClass('active')
            tree.data('status', status)
            zTreeObj = $.fn.zTree.init(tree, setting, znodes(data, status));
            check_action()

        })
        .fail(function(response) {
            var data = response.responseJSON
            console.log('fail', data)
            $('#sync_error').show()
            $('#sync_loading').addClass('sync_hidden')
            $('#sync_error_details').html(data.stacktrace)
        })

        
    $('#displayall').change(function() {
        console.log('change')
        var state = $(this).get(0).checked
        console.log(state)
        var tree = $('.ztree')
        if (!state) tree.addClass('hidenodes')
        else tree.removeClass('hidenodes')
    });
    
    var check_action = function(e) {
        console.log('check', $('.checkbox_true_full').length)
	    if ($('.checkbox_true_full').length) 
		    $('.btn-action-synchro').removeClass('disabled')
	    else
		    $('.btn-action-synchro').addClass('disabled');
	
    };
		  
		  
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
