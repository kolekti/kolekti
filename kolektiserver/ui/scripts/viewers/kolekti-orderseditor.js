function orderseditor() {    
    this.guidersid = new Array();
}

orderseditor.prototype=new kolekti_editor;

// Load resource
orderseditor.prototype.fetch_resource = function() {
    var c=new ajax(this.url);
    c.setParameter("viewer",this.viewname);
    c.setHeader('KolektiContext','orderseditor');
    var content=c.syncget();

    var div = document.createElement('div');
    div.innerHTML=content.text;
    this.content.appendChild(div);

    this.init_event();
    this.init_selecttrame();
    this.init_dnd();
}

//Init event listener
orderseditor.prototype.init_event = function() {
    var me = this;
    kolekti.listen('resource-detached-view',function(arg){me.detached_view(arg);return true;},this.context.id);
    kolekti.listen('publish',function(arg){me.publish(arg, false);return true;},this.context.id);
    kolekti.listen('publish-with-master',function(arg){me.publish(arg, true);return true;},this.context.id);
    this.init_enabled();
    this.init_notify();
}

// Initialisation of content
orderseditor.prototype.init_dnd = function() {
    var me = this;

    if(window.location.href.search(/publish=1/) > -1)
        this.publish();

    var addprofile = $(this.content).find("p.addprofile button")[0];
    addprofile.addEventListener("click", function() {me.additem(addprofile.parentNode, "profile");}, false);

    var addscript = $(this.content).find("p.addscript button")[0];
    addscript.addEventListener("click", function() {me.additem(addscript.parentNode, "script");}, false);
    
}

orderseditor.prototype.init_enabled = function() {
    var inp, del, item;

    var profiles = $(this.content).find("div.profile");
    for(var i=0; i<profiles.length; i++) {
        item = profiles[i];
        inp = $(item.parentNode).find("div.actions input[name='enabled']")[0];
        this.init_enabled_event(inp, item);
        del = $(item.parentNode).find("div.actions button[class='delete']")[0];
        this.init_deleted_event(del, item.parentNode);
    }

    var scripts = $(this.content).find("div.script");
    for(var i=0; i<scripts.length; i++) {
        item = scripts[i];
        inp = $(item.parentNode).find("div.actions input[name='enabled']")[0];
        this.init_enabled_event(inp, item);
        del = $(item.parentNode).find("div.actions button[class='delete']")[0];
        this.init_deleted_event(del, item.parentNode);
    }
}

orderseditor.prototype.init_enabled_event = function(inp, div) {
    var me = this;
    inp.addEventListener("click", function(e) {me.change_inputs_states(inp, div);}, false);

    // init first state
    this.change_inputs_states(inp, div);
}

orderseditor.prototype.init_deleted_event = function(del, item) {
    del.addEventListener("click", function(e) {item.parentNode.removeChild(item);}, false);
}

orderseditor.prototype.change_inputs_states = function(inp, div) {
    var curinp;

    var inputs = $(div).find("input");
    for(var i=0; i<inputs.length; i++) {
        curinp = inputs[i];
        if(inp.checked)
            curinp.disabled = false;
        else
            curinp.disabled = true;
    }

    var selects = $(div).find("select");
    for(var i=0; i<selects.length; i++) {
        curinp = selects[i];
        if(inp.checked)
            curinp.disabled = false;
        else
            curinp.disabled = true;
    }
}

//Show / Hide select browser
orderseditor.prototype.init_selecttrame = function() {
    var me = this;
    var p = $(this.content).find('p.tramechoose')[0];
    // Toggle class
    p.addEventListener("click", function(e) {me.show_hide_browser(p);}, false);
}

//Change text and class to display browser
orderseditor.prototype.show_hide_browser = function(p) {
    var span = p.getElementsByTagName('span');
    $(span[0]).toggleClass("ui-icon-minusthick").toggleClass("ui-icon-plusthick");

    var iframe = p.parentNode.getElementsByTagName('iframe')[0];
    if(iframe.style.display == "none") {
        iframe.style.display = "inline";
        span[1].textContent = i18n("[0315]Cacher l'explorateur");
    } else {
        iframe.style.display = "none";
        span[1].textContent = i18n("[0316]Afficher l'explorateur");
    }
}

// Make notification change for each input
orderseditor.prototype.init_notify = function() {
    var inputs = this.content.getElementsByTagName('input');
    for(var i=0; i<inputs.length; i++) {
        var inp = inputs[i];
        if(inp.type == "text")
            this.change_input(inp, 'keyup');
        else if(inp.type == "checkbox")
            this.change_input(inp, 'change');
    }

    var select = this.content.getElementsByTagName('select');
    for(var i=0; i<select.length; i++) {
       var s = select[i];
       if(s.name != "script")
          this.change_input(s, 'change');
    }

    var btn = this.content.getElementsByTagName('button');
    for(var i=0; i<btn.length; i++) {
        this.change_input(btn[i], 'click');
    }
}

// Set event type to notify changed
orderseditor.prototype.change_input = function(input, type) {
    var me = this;
    this.init_input(input);
    input.addEventListener(type,function(e){kolekti.notify('editor-resourcemodified',null,me.context.id);},false);
}

// Init input with param
orderseditor.prototype.init_input = function(input) {
    var me = this;

    if(input.name=='trameurl') {
        var value = this.get_trame_param();
        if(value)
            input.value=value;
        return;
    }
    if(input.parentNode.className=="formselect" || input.parentNode.parentNode.className=="parameter" || input.name == "suffix") {
        var fv = $(input.parentNode.parentNode).find(".formvalue");
        if(fv.length > 0) {
            this.select_param_option(input, fv[0]);
            input.addEventListener('change',function(e){me.select_param_option(input, fv[0])},false);
        }
        return;
    }
}

// Show/Hide options of param
orderseditor.prototype.select_param_option = function(input, fv) {
    if(input.checked)
        fv.style.display = "inline";
    else
        fv.style.display = "none";
}

// Get trame param if exist
orderseditor.prototype.get_trame_param = function() {
    var ref = window.location.href;
    var splitTrame = ref.split('trame=');
    if(splitTrame.length == 1)
        return null;
    return decodeURI(splitTrame[1].split('&')[0]);
}

// Create new profile element
orderseditor.prototype.additem= function(elem, type) {
    var req, pp;
    var props = [];

    var select = $(elem).find('select')[0];

    var conn = new ajaxdav(this.url);
    conn.setParameter("viewer",this.viewname);
    conn.setHeader("KolektiData",select.value);
    conn.setHeader('KolektiContext','orderseditor');
    conn.setHeader('KolektiForceView','1');
 
    if(type == "script")
        props.push({ns:'kolekti:scripts',propname:'script'});
    else
        props.push({ns:'kolekti:configuration',propname:'profile'});

    req = conn.PROPFIND(props);

    if(req.result.status == "207") {
       var xpr = req.object;
       while (xpr.nextResponse()) {
            // Add new script
            pp=xpr.get_prop('kolekti:scripts','script');
            if (pp.status=='200' && pp.content.firstChild)
                this.init_additem(elem, pp.content.firstChild, type);
            // Add new profile
            pp=xpr.get_prop('kolekti:configuration','profile');
            if (pp.status=='200' && pp.content.firstChild)
                this.init_additem(elem, pp.content.firstChild, type);
        }
    }
    
}

// Init event for a new item
orderseditor.prototype.init_additem= function(elem, content, type) {
    var item = elem.parentNode.insertBefore(content, elem);
    var inp = $(item).find("div.actions input[name='enabled']")[0];
    this.init_enabled_event(inp, $(item).find("div."+type)[0]);
    var del = $(item).find("div.actions button[class='delete']")[0];
    this.init_deleted_event(del, item);

    var inputs = item.getElementsByTagName('input');
    for(var i=0; i<inputs.length; i++)
        this.init_input(inputs[i]);
}

orderseditor.prototype.init_details = function(sp, i) {
    var me = this;
    var title;
    var details = $(sp.parentNode).find('.profiledetails')[0];

    kolekti.create_guider(this.context.id+i, sp.getElementsByTagName("label")[0], details.innerHTML, i18n("[0317]Détails du profil"), 7);
    kolekti.update_guiders(this.context.domview);

    sp.parentNode.removeChild(details);
    
    if(window.location.href.search(/mode=detached/) > -1)
        sp.removeChild($(sp).find('.profilelink')[0]);
}

// Generate xml order
orderseditor.prototype.get_data = function() {
    var val, code, min, max;
    var me = this;

    var oid = this.url.split('/').pop().split(".xml")[0];
    var xmlbuf='<order id="'+oid+'">';

    var pubdir = $(this.content).find(".pubdir input[name='pubdir']")[0];
    xmlbuf += '<pubdir value="'+pubdir.value+'"/>';

    var pubtitle = $(this.content).find(".pubtitle input[name='pubtitle']")[0];
    xmlbuf += '<pubtitle value="'+pubtitle.value+'"/>';

    var trame = $(this.content).find("div.trames input[name='trameurl']")[0];
    xmlbuf += '<trame value="@trames/'+trame.value+'" />';

    xmlbuf += '<profiles>';
    var profiles = $(this.content).find("fieldset div.profile");
    for(var i=0; i<profiles.length; i++) {
        var p = profiles[i];
        var enabled = +($(p.parentNode).find("div.actions input[name='enabled']")[0].checked);
        xmlbuf += '<profile enabled="'+enabled+'">';
        xmlbuf += '<label>'+$(p).find("input[name='label']")[0].value+'</label>';
        xmlbuf += '<criterias>';
        var criterias = $(p).find(".criteria span.formvalue");
        for(var j=0; j<criterias.length; j++) {
            var crit = criterias[j];
            var values = crit.getElementsByTagName("select");
            var checked = +($(crit.parentNode).find("input[name='enabled']")[0].checked);
            // enum criteria
            if(values.length == 1) {
                val = values[0].options[values[0].selectedIndex].value;
                code = values[0].name;
            } else {
                values = crit.getElementsByTagName("input");
                val = values[0].value;
                code = values[0].name;
            }

            xmlbuf += '<criteria checked="'+checked+'" code="'+code+'" value="'+val+'" />';
        }
        xmlbuf += '</criterias>';
        xmlbuf += '</profile>';
    }
    xmlbuf += '</profiles>';

    xmlbuf += '<scripts>';
    var scripts = $(this.content).find("fieldset div.script");
    for(var i=0; i<scripts.length; i++) {
        var s = scripts[i];
        var enabled = +($(s.parentNode).find("div.actions input[name='enabled']")[0].checked);
        var ninp = $(s).find("input[name='name']")[0];
        xmlbuf += '<script name="'+ninp.value+'" enabled="'+enabled+'">';
        var suf = $(s).find(".suffix")[0];
        var sufinp = suf.getElementsByTagName("input");
        var sufenabled = +(sufinp[0].checked);
        xmlbuf += '<suffix enabled="'+sufenabled+'">'+sufinp[1].value+'</suffix>';
        xmlbuf += '<parameters>';
        var params = $(s).find(".parameter");
        for(var j=0; j<params.length; j++) {
            var p = params[j];
            var pinp = p.getElementsByTagName("input");
            if(pinp.length > 0) {
                var val = pinp[0].value;
                if(pinp[0].type == "checkbox")
                    val = +pinp[0].checked;
                xmlbuf += '<parameter name="'+pinp[0].name+'" value="'+val+'" />';
            } else {
                pinp = p.getElementsByTagName("select");
                if(pinp.length > 0)
                    xmlbuf += '<parameter name="'+pinp[0].name+'" value="'+pinp[0].options[pinp[0].selectedIndex].value+'" />';
            }
        }
        xmlbuf += '</parameters>';
        xmlbuf += '</script>';
    }
    xmlbuf += '</scripts>';

    xmlbuf += '</order>';

    return xmlbuf;
}

// Check if resource if save before detached it
orderseditor.prototype.detached_view = function(arg) {
    if (!this.statesaved){
        if (confirm(i18n("[0318]%(title)s a été modifié, voulez-vous sauvegarder avant ?", {'title':this.context.title.textContent}))) {
            this.do_save_detached();
            this.open_detached_view(arg.url);
        }
    } else {
        this.open_detached_view(arg.url);
    }
}

// Save resource before detached
orderseditor.prototype.do_save_detached=function() {
    if (this.send_data()) {
    this.statesaved=true;
    this.save_action_button.icon.setAttribute('src','/_lib/kolekti/icons/icon-save-on.png');
    this.save_action_button.elt.setAttribute('class','viewershortnameaction enabled');
    this.etag=this.get_etag();
    if(this.sidebar)
        kolekti.notify('sidebar-refresh',this.sidebar.dom,this.sidebar.id);
    }
}

// Open order on new window
orderseditor.prototype.open_detached_view = function(url) {
    // Store current tab in session
    var arg = new Object();
    arg['urlid'] = this.context.id;
    kolekti.notify('resource-delete',arg,null);
    window.open(url+"?viewer=orderseditor&mode=detached", this.context.title.textContent, config='height=400, width=800, toolbar=no, menubar=no, scrollbars=no, resizable=no, location=no, directories=no, status=no');
}

// Start publication
orderseditor.prototype.publish = function(arg, genmaster) {
    if(this.check_order()) {
        var me = this;
        var d = new Date();
        var master = +genmaster;
        this.publishwindow = window.open(this.url+"?viewer=orderseditor&mode=publishorder&master="+master, this.context.title.textContent+"publish"+d.getUTCMilliseconds(), config='height=400, width=auto, toolbar=yes, menubar=yes, scrollbars=yes, resizable=yes, location=no, directories=no, status=no');

        if(genmaster)
            this.publishwindow.addEventListener("load", function() {me.init_publishmaster();},false);
        else
            this.publishwindow.addEventListener("load", function() {me.send_publish(false);},false);
    } else {
        alert(i18n("[0337]Erreur! Lancement non conforme. Veuillez vérifier la présence et le nom unique de vos profils et sorties."));
    }
}

orderseditor.prototype.send_publish = function(genmaster) {
    if(this.publishwindow) {
        var div = document.createElement("div");
        div.className = "publish_waiting";
        var img = document.createElement("img");
        img.setAttribute("src", "/_lib/kolekti/icons/wait.gif");
        img.setAttribute("alt", "...");
        div.appendChild(img);
        var p = document.createElement("p");
        p.textContent = i18n("[0354]Publication en cours");
        div.appendChild(p);
        this.publishwindow.document.body.appendChild(div);
        this.publishwindow.waiting = div;
    }
    var conn=new ajax(this.url);
    conn.setHeader('KolektiContext','orderseditor');
    conn.setParameter('KolektiData', this.get_data());
    if(genmaster) {
        conn.setParameter('genmaster', '1');
        conn.setParameter('mastername', this.mastername.value);
        if(this.filtermaster.filter.checked)
            conn.setParameter('filtermaster', this.filtermaster.data.value);
    }
    conn.setCallback(this.callback_log,3)
    conn.setCallback(this.callback_result,4)
    conn.setData(this);
    var req=conn.post();
}

orderseditor.prototype.check_order = function() {
    var lbl;
    var trame = $(this.content).find("div.trames input[name='trameurl']")[0];
    if(trame.value == "")
        return false;

    var profiles = $(this.content).find("fieldset div.profile");
    if (profiles.length == 0) {
        return false;
    } else {
        var hasprofile = false;
        var plabel = new Array();
        for(var i=0; i<profiles.length; i++) {
            lbl = $(profiles[i]).find("input[name='label']")[0].value;
            var enabled = $(profiles[i].parentNode).find("div.actions input[name='enabled']")[0].checked;
            if(enabled && (lbl == "" || plabel[lbl]))
                return false;
            if(enabled) {
                plabel[lbl] = true;
                hasprofile = true;
            }
        }
        if(!hasprofile)
            return false;
    }

    var scripts = $(this.content).find("fieldset div.script");
    if (profiles.length == 0) {
        return false;
    } else {
        var hascript = false;
        var slabel = new Array();
        for(var i=0; i<scripts.length; i++) {
            lbl = $(scripts[i]).find("input[name='name']")[0].value;
            var enabled = +($(scripts[i].parentNode).find("div.actions input[name='enabled']")[0].checked);
            var suf = $(scripts[i]).find(".suffix")[0];
            var sufinp = suf.getElementsByTagName("input");
            var sufenabled = sufinp[0].checked;
            if(enabled && ((!sufenabled && slabel[lbl]) || (sufenabled && slabel[lbl+sufinp[1].value])))
                return false;
            if(enabled && sufenabled)
                slabel[lbl+sufinp[1].value] = true;
            else if(enabled)
                slabel[lbl] = true;
            if(enabled)
                hascript = true;
        }
        if(!hascript)
            return false;
    }
    return true;
}

orderseditor.prototype.callback_log = function(res,me) {
    var ldiv=$(me.publishwindow.document).find(".publishorderviewer .publisher")[0];
    ldiv.style.display='block';
    $(ldiv).html(res.text);
    var publishorderviewer = $(me.publishwindow.document).find(".publishorderviewer")[0];
    publishorderviewer.scrollTop=ldiv.scrollHeight;
}

orderseditor.prototype.callback_result = function(res,me) {
    try {
        var ldiv=$(me.publishwindow.document).find(".infos")[0];
        ldiv.style.display='none';
        ldiv=$(me.publishwindow.document).find(".publication_log")[0];
        ldiv.style.display='none';
        var mdivs=$(me.publishwindow.document).find(".master");
        if(mdivs.length > 0)
            mdivs[0].style.display='none';
        var resdiv = me.publishwindow.document.createElement("div");
        resdiv.className = "publication_result";
        ldiv.parentNode.appendChild(resdiv);
        resdiv.innerHTML=res.text;
        me.format_links(resdiv);
        me.format_masterlink(resdiv);
        resdiv.style.display='block';
        var publishorderviewer = $(me.publishwindow.document).find(".publishorderviewer")[0];
        publishorderviewer.scrollTop = 0;
    } catch(err) {}
    if(me.publishwindow.waiting)
        me.publishwindow.waiting.parentNode.removeChild(me.publishwindow.waiting);
}

orderseditor.prototype.format_links = function(div) {
    var divs = $(div).find('.profile');
    for(var i=0; i<divs.length; i++) {
        var d =divs[i];
        var dd = document.createElement('div');
        dd.className = 'links';
        $(d).find(".link").each(function() {
            var child = this;
            this.parentNode.removeChild(this);
            dd.appendChild(child);
        });

        if(d.firstChild)
            this.attached_profile(d, dd);
    }
}

orderseditor.prototype.format_masterlink = function(div) {
    var mlinks = $(div).find(".masterlink");
    if(mlinks.length > 0) {
        var mlink = mlinks[0];
        var infos = $(div).find(".infos")[0];
        infos.appendChild(mlink);
    }
}

orderseditor.prototype.attached_profile = function(d, dd) {
    var me = this;
    d.firstChild.addEventListener('click',function(e){me.profile_section(d.firstChild)},false);
    d.insertBefore(dd, d.firstChild.nextSibling);

    if($(d).find('.result .error').length > 0) {
        $(d.firstChild.firstChild).toggleClass("ui-icon-minusthick").toggleClass("ui-icon-plusthick");
        $(d).find('.result')[0].style.display = "block";
        d.firstChild.firstChild.nextSibling.className = 'error';
    } else {
        $(d).find('.result')[0].style.display = "none";
        d.firstChild.firstChild.nextSibling.className = 'success';
    }
}

orderseditor.prototype.profile_section = function(div) {
    $(div.firstChild).toggleClass("ui-icon-minusthick").toggleClass("ui-icon-plusthick");
    var res = $(div.parentNode).find('.result')[0];
    if(res) {
        if(res.style.display=='block')
            res.style.display = 'none';
        else
            res.style.display = 'block';
    }
}

orderseditor.prototype.action_args = function(action) {
    var args=new Object();
    if(action=="save_as") {
        var comps=this.url.split('/')
        var f=comps.pop();
        var fc=f.split('.');
        args.dirname=comps.join('/');
        var ext = fc.pop();
        if(ext == '_')
            ext = "xml";
        args.extension=ext;
        args.resname=decodeURI(fc.join('.'));
    }
    return args;
}

orderseditor.prototype.can_save = function() {
    var comps=this.url.split('/');
    var f=comps.pop();
    if(f == '_')
        return false;
    return kolekti.uid == this.get_owner_uid();
}

orderseditor.prototype.quit_page = function(arg) {
    kolekti.remove_guiders(this.guidersid);
    return this.statesaved;
}

/* publish master */
orderseditor.prototype.init_publishmaster = function() {
    var me = this;
    var trame = $(this.content).find("div.trames input[name='trameurl']")[0];
    this.mastername  = $(this.publishwindow.document).find("input[name='mastername']")[0];
    this.mastername.value = trame.value.split('.xml')[0]+'_';

    this.filtermaster = {};
    var formselect = $(this.publishwindow.document).find(".formselect input");

    for(var i=0; i<formselect.length; i++) {
        var fs = formselect[i];
        var fv = $(fs.parentNode.parentNode).find(".formvalue input");
        if(fv.length > 0) {
            fs.addEventListener('change',function(e){me.select_param_option(fs, fv[0].parentNode)},false);
            if(fv[0].name == "filtermaster")
                this.filtermaster = {'filter': fs, 'data': fv[0]};
        }
    }

    try {
        var btncopy = $(this.publishwindow.document).find("button.copyfilter")[0];
        var selcopy = $(this.publishwindow.document).find("select[name='copyfilter']")[0];
        btncopy.addEventListener('click', function(e) {me.copy_filter(selcopy, me.filtermaster.data);}, false);
    } catch(err) {}

    var btn = $(this.publishwindow.document).find(".submitform button")[0];
    btn.addEventListener('click', function(e) {me.send_publish(true);}, false);
}

orderseditor.prototype.copy_filter = function(src, dst) {
    var val = src.options[src.selectedIndex].value;
    dst.value = val;
}
