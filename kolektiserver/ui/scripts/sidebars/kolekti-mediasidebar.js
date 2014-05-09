
function kolekti_mediasidebar(id, context) {
    this.id=id;
    this.context=context;
    this.properties = new Array();
    this.dom = null;
    this.section_state = new Object();
}

kolekti_mediasidebar.prototype=new kolekti_sidebar;

kolekti_mediasidebar.prototype.refresh=function(sidebar) {
    var child, e;
    var me=this;
    this.properties.push({ns:'kolekti:medias',propname:'heading'});
    sidebar.innerHTML = "";
    var conn=new ajaxdav(this.context.currenttab.url);
    conn.setHeader('KolektiForceView', '1');
    var req=conn.PROPFIND(this.properties,0); 

    if(req.result.status == "207") {
        var xpr = req.object;
        while (xpr.nextResponse()) {
            // Format usage case and init event
            pp=xpr.get_prop('kolekti:medias','usage');
            if (pp.status=='200' && pp.content.firstChild) {
                e = sidebar.appendChild(pp.content.firstChild);
                child = e.getElementsByTagName('li');
                for(var i=0; i<child.length; i++) {
                    this.init_usage(child[i]);
                }
            }
        }

        var titles = sidebar.getElementsByTagName("h3");
    }
    this.init_ui();
}

/* init event for usage case */
kolekti_mediasidebar.prototype.init_usage=function(elt) {
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
        var splitModUrl =  arg.url.split('/modules/');
        window.location = splitModUrl[0]+'/modules?open='+splitModUrl[1]; }, false);
}
