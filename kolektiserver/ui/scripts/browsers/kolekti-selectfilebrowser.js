function selectfilebrowser(id) {
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

selectfilebrowser.prototype=new kolekti_browser;

selectfilebrowser.prototype.init_ui_callback = function(req,tab) {
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

selectfilebrowser.prototype.click_select_file= function(e) {
    e.stopPropagation();
    this.selection.set_selection(e.target.parentNode);

    var url = e.target.parentNode.kolekti.url;

    var file = "";
    var splitpath = url.split('/');
    for(var i=4; i<splitpath.length; i++) {
        if(i > 4)
            file += "/";
        file +=splitpath[i];
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
        if(inp.getAttribute('id') == "selectfile") {
            inp.value = decodeURI(file);    
            break;
        }
    }
}
