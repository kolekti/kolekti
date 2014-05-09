function sheetsviewer() {
}

sheetsviewer.prototype = new kolekti_viewer;

sheetsviewer.prototype.init = function(viewname, tab) {
    this.context=tab;
    this.viewname=viewname;
    this.url=this.context.url;
    this.version=this.context.version;
    this.load();
    var me=this;
    kolekti.listen('resource-refresh-sheets', function(arg) {return me.cb_refresh_sheet(arg);}, this.context.id);
    kolekti.listen('resource-refresh-xmlsheets', function(arg) {return me.cb_refresh_xmlsheets(arg);}, this.context.id);
}

// Generate xml sheet file
sheetsviewer.prototype.cb_refresh_sheet = function(arg) {
    // Display progress icon during send data
    var action = this.vieweractions.firstChild;
    if(action) {
        progress = document.createElement('span');
        progress.className = "progress";
        action.appendChild(progress);
    }

    var conn = new ajaxdav(arg.url);
    conn.setParameter('refreshsheets', '1');
    var res = conn.send('PUT');

    // Remove progress icon
    if(action)
        action.removeChild(progress);

    if(res.status == "200") {
        var splitUrl = arg.url.split('.');
        if(splitUrl.pop() == "xml") {
            kolekti.notify('resource-refresh-xmlsheets', arg, this.context.id);
        }
        return true;
    } else {
        alert(i18n("[0320]Erreur lors de la génération du fichier xml."));
        return false;
    }
}

// Refresh view
sheetsviewer.prototype.cb_refresh_xmlsheets = function(arg) {
    this.iframe.src = arg.url+"?viewer=sheetsviewer";
}
