
function kolekti_tramesidebar(id, context) {
    this.id=id;
    this.context=context;
    this.properties = new Array();
    this.commitmsg = null;
    this.dom = null;
    this.section_state = new Object();
}

kolekti_tramesidebar.prototype=new kolekti_sidebar;

kolekti_tramesidebar.prototype.refresh=function(sidebar) {
    var child, e;
    var me=this;
    this.properties.push({ns:'kolekti:trames',propname:'heading'});
    sidebar.innerHTML = "";
    var conn=new ajaxdav(this.context.currenttab.url);
    conn.setHeader('KolektiForceView', '1');
    var req=conn.PROPFIND(this.properties,0); 

    if(req.result.status == "207") {
        var xpr = req.object;
        while (xpr.nextResponse()) {
            // Format usage case and init event
            pp=xpr.get_prop('kolekti:trames','heading');
            if (pp.status=='200' && pp.content.firstChild) {
                e = sidebar.appendChild(pp.content.firstChild);
            }
            pp=xpr.get_prop('kolekti:trames','usage');
            if (pp.status=='200' && pp.content.firstChild) {
                e = sidebar.appendChild(pp.content.firstChild);
                child = e.getElementsByTagName('li');
                for(var i=0; i<child.length; i++) {
                    this.init_usage(child[i]);
                }
            }
            pp=xpr.get_prop('kolekti:trames','diagnostic');
            if (pp.status=='200' && pp.content.firstChild) {
                e = sidebar.appendChild(pp.content.firstChild);
            }
            pp=xpr.get_prop('kolekti:trames','notes');
            if (pp.status=='200' && pp.content.firstChild) {
                e = sidebar.appendChild(pp.content.firstChild);
                this.init_notes(e);
            }
        }
        var titles = sidebar.getElementsByTagName("h3");
    }
    this.init_ui();
}

/* init event for usage case */
kolekti_tramesidebar.prototype.init_usage=function(elt) {
    var arg = new Object();
    elt.setAttribute('style', 'cursor:pointer;');
    var childNode = elt.firstChild.firstChild;
    while(childNode) {
        if(childNode.className=="resid")
            arg.resid = childNode.textContent;
        else if(childNode.className=="url")
            arg.url = childNode.textContent;
        else if(childNode.className=="urlid")
            arg.urlid = childNode.textContent;
        childNode = childNode.nextElementSibling;
    }
    elt.addEventListener('click',function(e){
        var splitConfigUrl =  arg.url.split('/configuration/');
        window.location = splitConfigUrl[0]+'/configuration?open='+splitConfigUrl[1]; }, false);
}

/* init event for filterview case */
kolekti_tramesidebar.prototype.init_filterview=function(elt, child) {
    var arg = new Object();
    arg.url = this.context.currenttab.url;
    arg.filterview = elt;
    var resid = $("li[title='"+this.context.currenttab.url+"']").attr('id');
    child.addEventListener('change',function(e){kolekti.notify('resource-filter-view',arg,resid);},false);
}

/* init event for editing notes */ 
kolekti_tramesidebar.prototype.init_notes=function(elt) {
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
