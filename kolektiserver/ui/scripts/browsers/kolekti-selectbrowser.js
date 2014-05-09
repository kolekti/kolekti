function selectbrowser(id) {
    this.id=id;
    this.tabs=new Array();
    this.behaviors=new Array();
    this.actions=new Array();
    this.actionspara=null;
    //this.displayresource=this.show_restab;
    this.currenttab=null;
    this.currenttabid=null;
    this.rootdir=null;
    this.tabnb=0;
    this.selection=new kolekti_browser_selection();
}

selectbrowser.prototype=new kolekti_browser;

selectbrowser.prototype.init_ui_callback = function(req,tab) {
    if (req.result.status == 207) {
    if (this.has_property('kolekti:browser','mainbrowseractions',this.browserproperties)) {
        var actionsp=document.createElement('p');
        actionsp.className="browseractions";

        var browseractions=document.createElement('span');
        browseractions.className="mainbrowseractions";
        actionsp.appendChild(browseractions);
        
        var clientactions=document.createElement('span');
        clientactions.className="clientactions";
        actionsp.appendChild(clientactions);

        if(this.attach_tab_behavior(actionsp,req.object,tab.rootnode.url)) {
            this.rootdir.parentNode.insertBefore(actionsp, this.rootdir);
            this.actionspara=actionsp;
        }
    }
    }
}

//creates a file structure in the dom tree
selectbrowser.prototype.create_file_dom_structure=function(xpr,childnode) { }

selectbrowser.prototype.attach_file_behavior = function(node,props) { }

selectbrowser.prototype.click_select_file= function(e) {
    e.stopPropagation();
    this.selection.set_selection(e.target.parentNode);

    var url = e.target.parentNode.parentNode.kolekti.url;

    var dir = "";
    var splitdir = url.split('/');
    for(var i=4; i<splitdir.length; i++) {
        if(i > 4)
            dir += "/";
        dir +=splitdir[i];
    }

    var action;
    if(window == parent)
        action = document.getElementById('action_dialog_'+this.id);
    else
        action = document.getElementById(this.id);

    var inputs = action.getElementsByTagName('input');
    var inp;
    for(var i=0; i<inputs.length; i++) {
        inp = inputs[i];
        if(inp.getAttribute('id') == "selectdir") {
            inp.value = decodeURI(dir);
            break;
        }
    }
}
