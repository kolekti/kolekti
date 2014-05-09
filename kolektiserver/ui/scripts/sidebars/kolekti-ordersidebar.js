
function kolekti_ordersidebar(id, context) {
    this.id=id;
    this.context=context;
    this.properties = new Array();
    this.commitmsg = null;
    this.dom = null;
    this.section_state = new Object();
}

kolekti_ordersidebar.prototype=new kolekti_sidebar;

kolekti_ordersidebar.prototype.refresh=function(sidebar) {
    var child, e;
    var me=this;
    sidebar.innerHTML = "";
    var conn=new ajaxdav(this.context.currenttab.url);
    conn.setHeader('KolektiForceView', '1');
    var req=conn.PROPFIND(this.properties,0); 

    if(req.result.status == "207") {
        var xpr = req.object;
        while (xpr.nextResponse()) {
            pp=xpr.get_prop('kolekti:configuration','versions');
            if (pp.status=='200' && pp.content.firstChild) {
                e = sidebar.appendChild(pp.content.firstChild);
            }
            pp=xpr.get_prop('kolekti:configuration','notes');
            if (pp.status=='200' && pp.content.firstChild) {  
                e = sidebar.appendChild(pp.content.firstChild);
                this.init_notes(e);
        }
        }
        var titles = sidebar.getElementsByTagName("h3");
        //elt.parentNode.insertBefore(,elt);
    }
    this.init_ui();
}

/* init event for editing notes */ 
kolekti_ordersidebar.prototype.init_notes=function(elt) {
    var e=elt.getElementsByTagName('textarea').item(0);
    this.commitmsg = e;
    var b=elt.getElementsByTagName('button').item(0);
    if (b) {
    b.addEventListener('click',
               function(ev){
                   e.value=b.previousSibling.previousSibling.nodeValue;
               },
               false);
    }
}