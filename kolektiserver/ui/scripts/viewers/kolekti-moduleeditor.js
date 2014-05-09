function moduleeditor() {
}

moduleeditor.prototype=new kolekti_editor;

moduleeditor.prototype.fetch_resource = function() {
    var me=this;
    var c=new ajax(this.url);
    c.setHeader('KolektiContext','moduleeditor');
    c.setCallback(function(res){me.fetch_resource_callback(res)});
    c.get();
}

moduleeditor.prototype.fetch_resource_callback = function(res) {
    var me=this;
    if (res.status==200) {
        var div = document.createElement('div');
        div.className = "resource_iframe";
        var textarea = document.createElement('textarea');
        textarea.setAttribute('name', 'editor'+this.context.id);
        textarea.textContent = res.text;
        div.appendChild(textarea);
        this.content.appendChild(div);

    }
    this.contentactions.setAttribute('style', 'margin: 0;');
    /* Check if editor has already instantiate */
    var inst = CKEDITOR.instances['editor'+this.context.id];
    if(inst)
        CKEDITOR.remove(inst);
    this.cke=CKEDITOR.replace( 'editor'+this.context.id,  { customConfig : '/_lib/app/scripts/ckeditor/moduleeditor-config.js' });
    this.cke.on( 'change', function( e ){me.resourcemodified(e) } );
    kolekti.listen('quit-page',function(arg){return me.unload_editor(arg);},this.context.id);
}

moduleeditor.prototype.do_save=function() {
    // vérifier si y'a un lock
    // vérifer le etag
    var etag=this.get_etag();
    if (etag!=this.etag) {
    if(!confirm(i18n("[0309]La ressource a été modifiée sur le serveur, voulez-vous continuer ?")))
        return;
    }
    if (this.send_data(this.save_action_button)) {
    this.statesaved=true;
    this.save_action_button.icon.setAttribute('src','/_lib/kolekti/icons/icon-save-off.png');
    this.save_action_button.elt.setAttribute('class','viewershortnameaction enabled');
    this.etag=this.get_etag();
    if(this.sidebar)
        kolekti.notify('sidebar-refresh',this.sidebar.dom,this.sidebar.id);
    if(kolekti.svnrevision)
        kolekti.notify('svnrevision-change',{'url':this.url}, null);
    kolekti.notify('browser-refresh',{'url':this.url, 'file': true}, null);
    // Mise à jour de la version du module
    //this.version++;
    //this.updateproperties("version", "kolekti:modules", this.version);
    this.context.set_title(this.version);
    } else {
        alert(i18n("[0308]Echec lors de la sauvegarde"));
    }
}

moduleeditor.prototype.updateproperties = function(name,ns,value) {
    var xpr=this.context.properties.firstChild;
    while (xpr) {
    if (xpr.localName==name && xpr.namespaceURI==ns) {
        xpr.textContent=value;
    }
    xpr=xpr.nextSibling;
    }
    return null;
}

moduleeditor.prototype.get_data = function() {
    return this.cke.getData();
}

moduleeditor.prototype.resourcemodified = function(e) {
    if(this.cke.mode)
        kolekti.notify('editor-resourcemodified',null,this.context.id);
}

moduleeditor.prototype.unload_editor = function(e) {
    if (this.cke) {
    CKEDITOR.remove(this.cke);
    this.cke=null;
    }
    return true;
}
