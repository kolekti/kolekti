function configurationresview(id) {
    this.id=id;
    this.tabnb=0;
    this.tabs=new Array();
    this.actions=new Array();
    this.currenttab = null;
    this.initopen=new Array();
    this.context='viewer';
    this.overlay=true; // 
    //this.initevent();
}

configurationresview.prototype = new kolekti_resview;

//init tabs in session
configurationresview.prototype.initsession= function() {
    var props=[{ns:'kolekti:session',propname:'sessionvalue'}];
    var conn = new ajaxdav('/_session/'+this.id);
    var req=conn.PROPFIND(props,0); 
    if (req.result.status == 207) {
    var dirs=req.object;
    dirs.nextResponse();
    var p=dirs.get_prop('kolekti:session','sessionvalue');
    try {
        var tab=p.content.firstChild.firstChild;
        var re=new RegExp('^/projects/'+kolekti.project,'');
        while(tab) {
            var taburl = tab.getAttribute('url');
            if(taburl.search(re) >= 0) {
                this.addinitopen(taburl,
                         tab.getAttribute('urlid'),
                         tab.getAttribute('version'));
            }
            tab=tab.nextSibling;
        }
    }
    catch (e){}

    }
}

//create a new custom tab
configurationresview.prototype.custom_resource_tab= function(component,url,urlid,overlay) {    
    var fold = url.split('/configuration/')[1].split('/')[0];
    if(fold == "orders" || fold == "publication_profiles")
        return new kolekti_configuration_resource_tab(component,url,urlid,this.overlay,fold);
    return new kolekti_resource_tab(component,url,urlid,this.overlay);
}



function kolekti_configuration_resource_tab(component,url,id,overlay,foldtype) {
    this.id=id;
    this.url=url;
    this.parent=component;
    this.view=component;
    this.overlay=overlay;
    this.version=null;
    this.viewok=false;
    this.active=false;
    this.foldtype=foldtype;
    this.initevent();
}

kolekti_configuration_resource_tab.prototype = new kolekti_resource_tab;

kolekti_configuration_resource_tab.prototype.set_title = function(version) {
    this.version=version;
    var dname = this.gettextprop('displayname','DAV:');
    if(this.foldtype == "orders")
        dname = i18n("[0196]Lancement")+ " " + dname;
    else if(this.foldtype == "publication_profiles")
        dname = i18n("[0311]Profil de publication") + " " + dname;
    this.title.nodeValue=dname;
}
