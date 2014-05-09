function uploadmediasbrowser(id) {
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

uploadmediasbrowser.prototype=new kolekti_browser;

uploadmediasbrowser.prototype.initevent = function() {
    var me=this;    
    kolekti.listen('media-preview',function(arg){me.preview(arg);return true;}, null);
    kolekti.listen('media-select',function(arg){me.select();return true;}, null);
}

uploadmediasbrowser.prototype.preview = function(arg) {
    var splitUrl = arg.url.split('/');
    this.url=arg.url;
    this.urlid=arg.urlid; 
    this.resid=arg.resid;
    document.getElementById('media-preview').style.display="block";

    if(this.url.split('.')[1] == "swf")
        document.getElementById('media-preview-image').innerHTML='<object classid="clsid:d27cdb6e-ae6d-11cf-96b8-444553540000" codebase="http://download.macromedia.com/pub/shockwave/cabs/flash/swflash.cab#version=6,0,40,0"><param name="quality" value="high"/><param name="movie" value="'+this.url+'"/><embed pluginspage="http://www.macromedia.com/go/getflashplayer" quality="high" src="'+this.url+'" type="application/x-shockwave-flash"/></object>';
    else
        document.getElementById('media-preview-image').innerHTML='<img src="'+this.url+'" alt="'+this.url+'" title="'+splitUrl[splitUrl.length-1]+'" />';
}

uploadmediasbrowser.prototype.select = function() {
    window.opener.CKEDITOR.tools.callFunction(2, this.url, '');
    window.close();
}