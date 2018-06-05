
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

    var setup_tree = function(root, status) {
        root.find('li').each(function() {
            if ($(this).data('status') != status) {
                $(this).addClass('sync_hidden')
            }
        })
    }
    
    $.get('/sync/tree')
        .done(function(data) {

            main_status = $.map(data, function(dir) {
                return dir.__self.kolekti_status
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
            var div = $("<div>") 
            populate_tree(div, data)
            setup_tree(div, status)
            $('.sync_' + status +' .sync_tree').append(div)
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
