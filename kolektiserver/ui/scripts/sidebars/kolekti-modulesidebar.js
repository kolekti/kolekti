
function kolekti_modulesidebar(id, context) {
    this.id=id;
    this.context=context;
    this.properties = new Array();
    this.commitmsg = null;
    this.dom = null;
    this.section_state = new Object();
}

kolekti_modulesidebar.prototype=new kolekti_sidebar;

kolekti_modulesidebar.prototype.refresh=function(sidebar) {
    var child, e;
    var me=this;
    //this.properties.push({ns:'kolekti:modules',propname:'heading'});
    sidebar.innerHTML = "";
    var conn=new ajaxdav(this.context.currenttab.url);
    conn.setHeader('KolektiForceView', '1');
    var req=conn.PROPFIND(this.properties,0); 

    if(req.result.status == "207") {
        var xpr = req.object;
        while (xpr.nextResponse()) {
            // Format usage case and init event
            pp=xpr.get_prop('kolekti:modules','heading');
            if (pp.status=='200' && pp.content.firstChild) {
                e = sidebar.appendChild(pp.content.firstChild);
            }
            pp=xpr.get_prop('kolekti:modules','usage');
            if (pp.status=='200' && pp.content.firstChild) {
                e = sidebar.appendChild(pp.content.firstChild);
                child = e.getElementsByTagName('li');
                for(var i=0; i<child.length; i++) {
                    this.init_usage(child[i]);
                }
            }
            pp=xpr.get_prop('kolekti:modules','filterview');
            if (pp.status=='200' && pp.content.firstChild) {
                e = sidebar.appendChild(pp.content.firstChild);
                   this.init_filterview(e);    
            }
            pp=xpr.get_prop('kolekti:modules','versions');
            if (pp.status=='200' && pp.content.firstChild) {
                e = sidebar.appendChild(pp.content.firstChild);
            }
            pp=xpr.get_prop('kolekti:modules','diagnostic');
            if (pp.status=='200' && pp.content.firstChild) {  
                e = sidebar.appendChild(pp.content.firstChild);
            }
            pp=xpr.get_prop('kolekti:modules','notes');
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

/* init event for usage case */
kolekti_modulesidebar.prototype.init_usage=function(elt) {
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
        childNode = childNode.nextSibling;
    }
    elt.addEventListener('click',function(e){
        var splitTrameUrl =  arg.url.split('/trames/');
        window.location = splitTrameUrl[0]+'/trames?open='+splitTrameUrl[1]; }, false);
}

/* init event for filterview case */
kolekti_modulesidebar.prototype.init_filterview=function(elt) {
    var arg = new Object();
    arg.url = this.context.currenttab.url;
    arg.filterview = elt;
    var resid = $("li[title='"+this.context.currenttab.url+"']").attr('id');
    var reset = $(elt).find('.reset_section')[0];
    reset.addEventListener('click',function(e){kolekti.notify('resource-filter-reset-view',arg,resid);},false);
    child = elt.getElementsByTagName('select');
    for(var i=0; i<child.length; i++) {
        child[i].addEventListener('change',function(e){kolekti.notify('resource-filter-view',arg,resid);},false);
    }
}

/* init event for editing notes */ 
kolekti_modulesidebar.prototype.init_notes=function(elt) {
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