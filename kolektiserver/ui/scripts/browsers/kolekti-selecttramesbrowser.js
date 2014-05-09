function selecttramesbrowser(id) {
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

selecttramesbrowser.prototype=new kolekti_browser;

selecttramesbrowser.prototype.initevent = function() {
    var me=this;    
    kolekti.listen('select-item',function(arg){me.select_item(arg);return true;},null);
}

selecttramesbrowser.prototype.init_ui_callback = function(req,tab) {
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

// display select item on resource view
selecttramesbrowser.prototype.select_item = function(arg) {
    var viewer = parent.e.tab.domview;
    var inputs = viewer.getElementsByTagName("input");
    for(var i=0; i<inputs.length; i++) {
        var input=inputs[i];
        if(input.name == "trameurl") {
            input.value=decodeURIComponent(arg.url.split('/trames/')[1]);
            parent.kolekti.notify('trame-change',input,parent.e.tab.id);
            parent.kolekti.notify('editor-resourcemodified',null,parent.e.tab.id);
            break;
        }
    }

    this.highlight(arg);
}

// Attached event selectitem
selecttramesbrowser.prototype.attach_file_behavior = function(node,props) {
    node.domnode.style.cursor="pointer";
    this.set_behavior(node,"selectitem",node.domnode); 
}
