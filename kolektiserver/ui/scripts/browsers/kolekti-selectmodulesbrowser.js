function selectmodulesbrowser(id) {
    this.id=id;
    this.tabs=new Array();
    this.behaviors=new Array();
    this.actions=new Array();
    this.dirstate=new Array();
    this.currenttab=null;
    this.currenttabid=null;
    this.tabnb=0;
    this.selection=new kolekti_browser_selection();
}

selectmodulesbrowser.prototype=new kolekti_browser;

selectmodulesbrowser.prototype.initevent = function() {
    var me=this;
    kolekti.listen('module-preview',function(arg){me.preview(arg);return true;}, null);
    kolekti.listen('module-select',function(arg){me.select();return true;}, null);
}

selectmodulesbrowser.prototype.preview = function(arg) {
    this.url=arg.url;
    this.urlid=arg.urlid; 
    this.resid=arg.resid;
    document.getElementById('module-preview').style.display="block";
    document.getElementById('module-preview-content').innerHTML = '<iframe src="'+this.url+'"><!-- iframe content --></iframe>';
}

selectmodulesbrowser.prototype.select = function() {
    window.opener.CKEDITOR.tools.callFunction(2, this.url, '');
    window.close();
}