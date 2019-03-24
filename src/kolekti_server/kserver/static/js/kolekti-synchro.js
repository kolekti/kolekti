var translations = {
    'dir' : 'dossier',
    'file': 'fichier',
    'modified' : 'modifié',
    'deleted': 'supprimé',
    'added' : 'nouveau',
    'unversionned': 'non versionné',
    'missing':'absent',
    'normal' : 'inchangé',
    'replaced':'remplacé',
    'merged':'fusionné',
    'conflicted':'en conflit',
    'ignored':'ignoré',
    'obstructed':'recouvert',
    'external':'externe',
    'incomplete':'incomplet'
}

$(document).ready(function() {
    
    var myOnExpand = function(event, treeId, treeNode) {
        console.log('expand')
        console.log(treeNode)
        
    };
            
    var myOnCheck = function(event, treeId, treeNode) {
        check_action(treeNode.checked?1:0)
    };
            
    var myOnClick = function(event, treeId, treeNode) {
        if (treeNode.status == treestatus) {
            $('#syncdetails .sync-det-type').html(translations[treeNode.ktype])
            $('#syncdetails .sync-det-name').html(treeNode.name)
            $('#syncdetails .sync-det-wstatus').html(translations[treeNode.kwstatus])
            $('#syncdetails .sync-det-rstatus').html(translations[treeNode.krstatus])
            $('#syncdetails').show()
        } else {
            $('#syncdetails').hide()
        }
    };
    var myOnNodeCreated = function(event, treeId, treeNode) {
        $('#'  + treeNode.tId+ '_span').addClass('status-' + treeNode.status)
        $('#'  + treeNode.tId+ '_span').addClass('hstatus-' + treeNode.hstatus)
        $('#'  + treeNode.tId+ '_span').addClass('wstatus-' + treeNode.kwstatus)
        var treestatus = $('#'  + treeNode.tId+ '_span').closest('.ztree').data('status')
        if (treeNode.hstatus != treestatus && treeNode.status != treestatus) {
            $('#'  + treeNode.tId+ '_span').closest('li').addClass('listitem-hiddable')
        }
        $('#'  + treeNode.tId+ '_span').closest('li').data('kpath', treeNode.kpath)
        
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
            if (!value.hasOwnProperty('__self')) {
                console.log("no __self for ", value)
                return;
            }
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
                        "kprstatus":value.__self.rpropstatus,
                        "kpwstatus":value.__self.wpropstatus,
                        
                        "status":node_status,
                        "hstatus":node_inherited_status,
                        "dstatus":node_detail_status,

                        "open":(node_inherited_status == status)?true:false,
                        "checked":(node_status == status || node_inherited_status == status)?true:false,
                        "chkDisabled":(node_status == status || node_inherited_status == status)?false:true,
                       }
            if (children.length)
                node.children = children
            nodes.push(node)
        });
        return nodes;
    }
    
    $('#syncdetails').hide()
    var treestatus;
    
    $.get(Urls.kolekti_sync_tree(kolekti.project))
        .done(function(data) {
            var main_status = data.__self.kolekti_inherited_status;
            console.log(main_status)
            
            var status;
            if (main_status == 'error'){
                status = "error";
                $('.sync_error').removeClass('sync_hidden')
            }
            else if (main_status == 'conflict'){
                status = "conflict";
                $('.sync_conflict').removeClass('sync_hidden')
            }
            else if (main_status == 'merge' ){
                status = "merge"
                $('.sync_merge').removeClass('sync_hidden')
            }
            else if (main_status == 'commit'){
                status = "commit"
                $('.sync_commit').removeClass('sync_hidden')
            }
            else if (main_status == 'update'){
                status = "update"
                $('.sync_update').removeClass('sync_hidden')
            }
            else {
                status = "ok"
                $('.sync_ok').removeClass('sync_hidden')
            }
            
            $('#sync_loading').addClass('sync_hidden')
            treestatus = status;
            if (status != "error"){ 
                var tree = $('.sync_' + status +' .sync_tree')
                tree.addClass('active')
                tree.data('status', status)
                $('.ztree').addClass('hidenodes')
                zTreeObj = $.fn.zTree.init(tree, setting, znodes(data, status));
                check_action(0)
            } else {
                $('#sync_error').removeClass('sync_hidden')
                $('#sync_loading').addClass('sync_hidden')
                $('#sync_error_details').html("Contactez le support technique de kolekti");
            }                
        })
        .fail(function(response) {
            var data = response.responseJSON
            $('#sync_error').removeClass('sync_hidden')
            $('#sync_loading').addClass('sync_hidden')
            $('#sync_error_details').html(data.stacktrace)
        })

        
    $('.displayall').change(function() {
        var state = $(this).get(0).checked
        var tree = $('.ztree')
        if (!state) tree.addClass('hidenodes')
        else tree.removeClass('hidenodes')
    });
    
    var check_action = function(supp) {
	    if ($('.checkbox_true_full').length + supp) 
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
        
//	    console.log("submit form");
        var path, form = $(this);
        $('.checkbox_true_full').each(function(e,i) {
            console.log('checkbox')
            path =  $(i).closest('li').data('kpath')
            form.append('<input type="hidden" name="fileselect" value="' + path + '">');
        });
	    $(window).trigger('kolekticlearcachedstatus');
	    $('#modal_processing').modal('show')
    })
		  
    $('#syncromsg').focus()    
})
