function projectresview(id) {
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

projectresview.prototype = new kolekti_resview;

//init tabs in session
projectresview.prototype.initsession= function() {
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