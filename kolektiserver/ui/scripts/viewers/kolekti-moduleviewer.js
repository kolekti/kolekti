function moduleviewer() {
}

moduleviewer.prototype=new kolekti_viewer;

moduleviewer.prototype.init = function(viewname, tab) {
    this.context = tab;
    this.viewname = viewname;
    this.url = this.context.url;
    this.version = this.context.version;
    this.load();
    var me = this;
    kolekti.listen('resource-filter-reset-view', function(arg) {return me.cb_filter_reset_view(arg);}, this.context.id);
    kolekti.listen('resource-filter-view', function(arg) {return me.cb_filter_view(arg);}, this.context.id);
    //kolekti.listen('resource-movemodule',function(arg){me.mod_move(arg);return true;},null);
    kolekti.listen('resource-browser-refresh',function(arg){me.mod_browser_refresh(arg);return true;},this.context.id);
    kolekti.listen('resource-rename',function(arg){me.mod_rename(arg);return true;},this.context.id);
    kolekti.listen('resource-duplicate',function(arg){me.mod_duplicate(arg);return true;},this.context.id);
    kolekti.listen('browser-resource-change-view',function(arg){me.change_view(arg);return true;},null);
}

// Change view from browser action
moduleviewer.prototype.change_view = function(arg) {
    kolekti.notify('resource-change-view', arg, arg.urlid);
}

// Reset select criterias and filter view
moduleviewer.prototype.cb_filter_reset_view = function(arg) {
    var select = arg.filterview.getElementsByTagName('select');
    for(var i=0; i<select.length; i++) {
        select[i].selectedIndex = 0;
    }
    this.cb_filter_view(arg);
}

// Filter view with selected criterias
moduleviewer.prototype.cb_filter_view = function(arg) {
    var s, value, cl;
    var hascriterias = false;
    var me = this;
    var criterias = new Array();
    var select = arg.filterview.getElementsByTagName('select');
    for(var i=0; i<select.length; i++) {
        s = select[i];
        value = s.options[s.selectedIndex].value;
        if(value != "") {
            criterias[s.name] = s.options[s.selectedIndex].value;
            hascriterias = true;
        }
    }

    var doc = this.iframe.contentWindow.document.body;
    $(doc).find("*[class*='=']").each(function(e) {
        if(hascriterias) {
            cl = this.className.replace(/ /g,'');
            if (me.check_condition(cl, criterias))
                this.style.display = "block";
            else
                this.style.display = "none";
        } else {
            this.style.display = "block";
        }
    });

    $(doc).find("a").each(function(e) {
        cl = this.getAttribute('href');
        this.setAttribute('href',me.replace_condition(this, cl, criterias));
    });

    $(doc).find("img").each(function(e) {
        cl = this.getAttribute('src');
        this.setAttribute('src',me.replace_condition(this, cl, criterias));
    });

    return true;
}

// Rename current resource
moduleviewer.prototype.mod_rename = function(arg) {
    var ext = arg.url.split('.').pop();
    if(confirm(i18n("[0313]Attention : Ce module est potientiellement utilisé dans des trames, cette action peut provoquer des erreurs lors de la publication des trames. Souhaitez-vous continuer?"))) {
        var conn = new ajaxdav(arg.url);
        var surl = arg.url.split('/')
        surl.pop();
        var nurl = surl.join('/')+'/'+arg.modname+'.'+ext;

        conn.setHeader("Destination", nurl);
        var res = conn.MOVE();
        if(res.status == "207") {
            arg.url = nurl;
            this.get_moddata(arg);
            kolekti.notify('resource-display-rename',arg,this.context.id);
        } else {
            alert(i18n("[0314]Erreur lors du changement de nom du module"));
        }
    }
}

// Refresh browser and open new resource to duplicate action
moduleviewer.prototype.mod_duplicate = function(arg) {
    var splitUrl = arg.url.split('/');
    var path = splitUrl.slice(0, 4);
    var dir = arg.moddir;
    if(dir != "")
        dir += '/';
    arg.url = path.join('/')+'/'+dir+arg.modname+'.'+arg.url.split('.').pop();
    this.get_moddata(arg);
    kolekti.notify('browser-refresh',arg,null);
    kolekti.notify('resource-display-open',arg,null);
}

//Refresh browser
moduleviewer.prototype.mod_browser_refresh = function(arg) {
    kolekti.notify('browser-refresh',arg,null);
    this.change_moddir(arg);
    this.get_moddata(arg);
    kolekti.notify('resource-display-rename',arg,this.context.id);
}

// Change dir of url
moduleviewer.prototype.change_moddir = function(arg) {
    var path = arg.url.split('modules/')[0]+'modules/';
    path += arg.moddir;
    path += '/'+arg.url.split('/').pop();
    arg.url = path;
}

// Change resid of newmodule
moduleviewer.prototype.get_moddata = function(arg) {
    var conn = new ajaxdav(arg.url);
    var req=conn.PROPFIND([{ns:'kolekti',propname:'resourceid'}],0);
    if(req.result.status == "207") {
        var xpr = req.object;
        while (xpr.nextResponse()) {
            pp=xpr.get_prop('kolekti','resourceid');
            if (pp.status=='200' && pp.content.firstChild) {
                arg.urlid = pp.content.firstChild.textContent;
                if(arg.urlid.search(/[a-zA-Z]+_[a-zA-Z0-9]+/) < 0)
                    arg.urlid = this.context.id.split('_')[0]+'_'+arg.urlid;
            }
     }
 }
}

// Replace condition by value
moduleviewer.prototype.replace_condition = function(elt, link, crit) {
    if(elt.url && elt.url.src)
        link = elt.url.src;
    else {
        elt.url = new Object();
        elt.url.src = link;
    }

    for(c in crit) {
        var r = new RegExp('_'+c+'_', 'gi');
        link = link.replace(r, crit[c]);
    }

    return link;
}

// Check if condition is valid
moduleviewer.prototype.check_condition = function(expr, crit) {
    var cond = expr.split('=');
    var c = cond[0];

    var expr = expr.substr(cond[0].length+1, expr.length);

    var r1 = !(expr.search(/,/) < 0);
    var r2 = !(expr.search(/;/) < 0);
    var r3 = !(expr.search(/\\/) < 0);

    // if criteria not selected
    if(!crit[c] && !r1) {
        return true;
    } else if(!crit[c]) {
        if(cond.length > 2) {
            //NoticePapier,NoticeWeb, ZONE = WestEurope, EastEurope
            var ncond = cond[1].split(',').pop();
            if(ncond.search(/;/) < 0)
                return this.check_condition(expr.substr(cond[1].length-ncond.length, expr.length), crit);
            else
                return false;
        } else {
            return true;
        }
    }

    // SIMPLE condition
    if(!r1 && !r2 && !r3) {
        return crit[c] == cond[1];
    }
    // EXCLUDE condition
    else if(!r1 && !r2 && r3) {
        return this.check_condition_exclude(expr, crit, c, cond[1]).result;
    }
    // AND condition
    else if(!r1 && r2 && !r3) {
        return this.check_condition_and(expr, crit, c);
    }
    // AND + EXCLUDE conditions
    else if(!r1 && r2 && r3) {
        var pos1 = expr.search(/;/);
        var pos2 = expr.search(/\\/);
        if(pos1 < pos2) {
            return this.check_condition_and(expr, crit, c) && this.check_condition(expr.substr(pos2+1, expr.length), crit);
        } else {
            var exclu = this.check_condition_exclude(expr, crit, c, cond[1]);
            return exclu.result && this.check_condition(expr.substr(exclu.pos+1, expr.length), crit);
        }
    }
    // OR condition
    else if(r1 && !r2 && !r3) {
        return this.check_condition_or(expr, crit, c).result;
    } 
    // OR + EXCLUDE conditions
    else if(r1 && !r2 && r3) {
        var pos1 = expr.search(/,/);
        var pos2 = expr.search(/\\/);
        if(pos1 < pos2) {
            var cor = this.check_condition_or(expr, crit, c)
            return cor.result || this.check_condition(expr.substr(cor.pos, expr.length), crit);
        } else {
            var exclu = this.check_condition_exclude(expr, crit, c, cond[1]);
            return exclu.result || this.check_condition(expr.substr(exclu.pos+1, expr.length), crit);
        }
    }
    // OR + AND conditions
    else if(r1 && r2 && !r3) {
        var pos1 = expr.search(/,/);
        var pos2 = expr.search(/;/);
        if(pos1 < pos2)
            return this.check_condition_or(expr, crit, c) && this.check_condition(expr.substr(pos2+1, expr.length), crit);
        else
            return this.check_condition_and(expr, crit, c) && this.check_condition(expr.substr(pos1+1, expr.length), crit);
    } 
    // OR + AND + EXCLUDE conditions
    else if(r1 && r2 && r3) {
        var pos1 = expr.search(/,/);
        var pos2 = expr.search(/;/);
        var pos3 = expr.search(/\\/);
        if(pos1 < pos2 && pos1 < pos3) {
            if(pos2 < pos3)
                return this.check_condition_or(expr, crit, c) || this.check_condition(expr.substr(pos2+1, expr.length), crit);
            else
                return this.check_condition_or(expr, crit, c).result || this.check_condition(expr.substr(pos3+1, expr.length), crit);
        } else if(pos2 < pos1 && pos2 < pos3) {
            if(pos1 < pos3)
                return this.check_condition_and(expr, crit, c) && this.check_condition(expr.substr(pos1+1, expr.length), crit);
            else
                return this.check_condition_and(expr, crit, c) && this.check_condition(expr.substr(pos3+1, expr.length), crit);
        } else {
            var exclu = this.check_condition_exclude(expr, crit, c, cond[1]);
            return exclu.result && this.check_condition(expr.substr(exclu.pos+1, expr.length), crit);
        }
    }
    return false;
}

// Check EXCLUDE condition
moduleviewer.prototype.check_condition_exclude = function(expr, crit, cond, val) {
    var curpos = 0;
    var pos = expr.search(/\\/);

    var splitVal = val.substr(pos+1,val.length).split(",");
    if (!(expr.search(new RegExp(splitVal[splitVal.length-1]+"=")) < 0))
        splitVal.pop();

    for(var i=0; i<splitVal.length; i++) {
        if(crit[cond] == splitVal[i])
            return {'result': false, 'pos': 0};
        curpos += splitVal[i].length+1;
    }
    return {'result': true, 'pos': curpos};
}

// Check OR condition
moduleviewer.prototype.check_condition_or = function(expr, crit, cond) {
    var curval;
    var val = expr.split(/[a-zA-Z0-9]+=/)[0].split(',');
    var curpos = 0;
    for(i=0; i<val.length; i++) {
        curval = val[i];
        if(curval != "") {
            curval = curval.split(';')[0];
            if(crit[cond] == curval)
                return {'result': true, 'pos': 0};
            curpos+= curval.length+1;
        }
    }
    return {'result': false, 'pos': curpos};
}

// Check AND condition
moduleviewer.prototype.check_condition_and = function(expr, crit, cond) {
    var val = expr.split(/[a-zA-Z0-9]+=/)[0].split(';');
    return crit[cond] == val[0] && this.check_condition(expr.substr(val[0].length+1, expr.length), crit);
}


moduleviewer.prototype.init_fixed = function() {
    var me = this;
    var btn = document.getElementById("fixed_btn");
    btn.addEventListener("click", function(ev) { me.fixed_btn(window.location.pathname); }, false);
}

moduleviewer.prototype.fixed_btn = function(url) {
    var conn = new ajaxdav(url);
    conn.setHeader("KOLEKTICOMMIMSG", "Fixed module errors");
    conn.setParameter("fixed", "1");
    var res = conn.PUT();
    if(res.status == 200) {
        window.location.reload();
        window.parent.kolekti.notify('browser-refresh',{'url':url, 'file': true}, null);
        if(window.parent.kolekti.svnrevision)
            window.parent.kolekti.notify('svnrevision-change',{'url':url}, null);
    } else {
        alert(i18n("[0353]Echec lors de la correction des erreurs du module"))
    }
}
