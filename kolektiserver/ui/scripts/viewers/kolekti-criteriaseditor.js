function criteriaseditor() {
}

criteriaseditor.prototype=new kolekti_editor;

criteriaseditor.prototype.fetch_resource = function() {
    var c=new ajax(this.url);
    c.setParameter("viewer",this.viewname);
    c.setHeader('KolektiContext','criteriaseditor');
    var content=c.syncget();
    var div = document.createElement('div');
    div.innerHTML=content.text;
    this.content.appendChild(div);
    this.init_notify();
    this.init_dnd();
    //this.init_properties();
}

// Make notification change for each input
criteriaseditor.prototype.init_notify = function() {
    var inputs = this.content.getElementsByTagName('input');
    for(var i=0; i<inputs.length; i++) {
        var inp = inputs[i];
        if(inp.type == "text")
            this.change_input(inp, 'keyup');
    }
}

//Set event type to notify changed
criteriaseditor.prototype.change_input = function(input, type) {
    var me = this;
    input.addEventListener(type,function(e){kolekti.notify('editor-resourcemodified',null,me.context.id);},false);
}

criteriaseditor.prototype.init_dnd = function() {
    var me = this;

    $(this.content).find('.criteria').each(function(index) {
        for(var i=0; i<this.childNodes.length; i++) {
            var child = this.childNodes[i];
            if(child.nodeType == "1" && child.nodeName == "P") {
                me.criterias_actions(child);
            } else if(child.nodeType == "1" && child.nodeName == "DIV") {
                me.criterias_values(child);
            }
        }
    });

    var p = document.getElementById("btn_addcriterias");
    p.getElementsByTagName('span')[0].addEventListener("click", function(e){me.add_criteria(p);}, null);
}

// General action for criterias
criteriaseditor.prototype.criterias_actions = function(elem) {
    for(var i=0; i<elem.childNodes.length; i++) {
        var child = elem.childNodes[i];        
        if(child.nodeType == "1" && child.className == "criteria_type") {
            this.init_changetype(elem, child);
        } else if(child.nodeType == "1" && child.className == "criteria_delete") {
            this.init_del_criteria(elem.parentNode, child);
        }
    }
}

// Init event to change type of criteria
criteriaseditor.prototype.init_changetype = function(elem, child) {
    var me = this;
    var arg = new Object();
    arg['select'] = child.getElementsByTagName('select')[0];
    arg['elem'] = elem.parentNode;
    child.addEventListener("change", function(e){me.changetype_criteria(arg);}, null);
}

// Init event to delete criteria
criteriaseditor.prototype.init_del_criteria = function(elem, child) {
    var me = this;
    child.addEventListener("click", function(e){me.del_criteria(elem);}, null);
}

// Init event to add value of criteria
criteriaseditor.prototype.init_add_criteria_value = function(elem, child) {
    var me = this;
    child.addEventListener("click", function(e){me.add_criteria_value(elem);}, null);
}

// Actions on value data
criteriaseditor.prototype.criterias_values = function(elem) {
    for(var i=0; i<elem.childNodes.length; i++) {
        var child = elem.childNodes[i];
        if(child.nodeType == "1" && child.className=="btn_addvalue") {
            this.init_add_criteria_value(elem, child.getElementsByTagName('span')[0]);
        } else if(child.nodeType == "1" && child.nodeName == "P") {
            this.criterias_values(child);
        } else if(child.nodeType == "1" && child.className == "criteria_delete") {
            this.init_del_criteria(elem, child)
        }
    }
}

/* Add enum input */
criteriaseditor.prototype.addEnum = function() {
    var me = this;
    var p = document.createElement("p");

    var pcontent = '<span class="criteria_value"><label>' + i18n("[0160]Valeur") + ': </label><input type="text" name="value" /></span> ';
    pcontent += '<span class="criteria_code"><label>' + i18n("[0154]Code") + ': </label><input type="text" name="code" /></span> ';
    p.innerHTML = pcontent;

    // Create delete icon
    var sp_delete = document.createElement("span");
    sp_delete.className = "criteria_delete";
    var img_delete = document.createElement("img");
    img_delete.src = "/_lib/kolekti/icons/btn_close.png";
    img_delete.alt = "X";
    img_delete.title = i18n("[0161]Supprimer la valeur");
    sp_delete.addEventListener("click", function(e){me.del_criteria(p);}, null);
    sp_delete.appendChild(img_delete);

    p.appendChild(sp_delete);

    return p;
}

// Add int input
criteriaseditor.prototype.addInt = function(elem) {
    var p = document.createElement("p");

    // Create value input
    var pcontent = '<span class="criteria_min"><label>' + i18n("[0163]Min") + ': </label><input type="text" name="min" /></span> ';
    pcontent += '<span class="criteria_max"><label>' + i18n("[0164]Max") + ': </label><input type="text" name="max" /></span> ';
    p.innerHTML = pcontent;

    elem.appendChild(p);
}

// Add criteria
criteriaseditor.prototype.add_criteria = function() {
    var me = this;
    var div = document.createElement('div');
    div.className="criteria";
    var p = document.createElement("p");

    // Create value input
    var pcontent = '<span class="criteria_name"><label>' + i18n("[0079]Nom") + ': </label><input type="text" name="criteria_name" /></span> ';
    pcontent += '<span class="criteria_code"><label>' + i18n("[0154]Code") + ': </label><input type="text" name="criteria_code" /></span> ';
    pcontent += '<span class="criteria_type"><label>' + i18n("[0155]Type") + ': </label>';
    pcontent += '<select name="criteria_type"> \
                    <option selected="selected" value="text">' + i18n("[0156]Texte") + '</option> \
                    <option value="enum">' + i18n("[0157]Enumération") + '</option> \
                    <option value="int">' + i18n("[0158]Entier") + '</option> \
                 </select>';
    pcontent += '</span> ';
    p.innerHTML = pcontent;

    // Create delete icon
    var sp_delete = document.createElement("span");
    sp_delete.className = "criteria_delete";
    var img_delete = document.createElement("img");
    img_delete.src = "/_lib/kolekti/icons/btn_close.png";
    img_delete.alt = "X";
    img_delete.title = i18n("[0161]Supprimer la valeur");
    sp_delete.appendChild(img_delete);
    p.appendChild(sp_delete);
    div.appendChild(p);
    sp_delete.addEventListener("click", function(e){me.del_criteria(p.parentNode);}, null);

    document.getElementById("criterias").insertBefore(div, document.getElementById("btn_addcriterias"));

    // Attached select event
    var select = p.getElementsByTagName('select')[0];
    var arg = new Object();
    arg['select'] = select;
    arg['elem'] = p.parentNode;
    select.addEventListener("change", function(e){me.changetype_criteria(arg);}, null);
    kolekti.notify('editor-resourcemodified',null,this.context.id);
}

// Change type of criteria
criteriaseditor.prototype.changetype_criteria = function(arg) {
    var me = this;
    var crit = arg['elem'];    
    var type = $(arg['select']).context.value;

    var div = crit.getElementsByTagName('div');

    for(var i=0; i<div.length; i++) {
        var d = div[i];
        if(d.className == "criteriasvalues")
            crit.removeChild(d);
    }

    if(type == "enum") {
        var div = document.createElement("div");
        div.className = "criteriasvalues";
        var p = this.addEnum();
        div.appendChild(p);
        var btn = document.createElement("p");
        btn.className = "btn_addvalue";
        var sp = document.createElement("span");
        sp.textContent = i18n("[0162]Ajouter une valeur");
        btn.appendChild(sp);
        div.appendChild(btn);
        sp.addEventListener("click", function(e){me.add_criteria_value(div);}, null);
        crit.appendChild(div);
    } else if(type == "int") {
        var div = document.createElement("div");
        div.className = "criteriasvalues";
        this.addInt(div);
        crit.appendChild(div);
    }
    kolekti.notify('editor-resourcemodified',null,this.context.id);
}

// Delete criteria
criteriaseditor.prototype.del_criteria = function(arg) {
    arg.parentNode.removeChild(arg);
    kolekti.notify('editor-resourcemodified',null,this.context.id);
}

// Add value to criteria
criteriaseditor.prototype.add_criteria_value = function(arg) {
    var i = 0;
    var p = this.addEnum();
    var childs = arg.childNodes;
    var c = childs[arg.childNodes.length-1];
    while(i < childs.length && c.nodeType != 1) {
        c = childs[childs.length-(i+1)];
        i++;
    }
    arg.insertBefore(p, c);
    kolekti.notify('editor-resourcemodified',null,this.context.id);
}

// Generate xml file before save
criteriaseditor.prototype.get_data=function() {
    var content = document.getElementById("criterias").innerHTML;
    var xml = "<criterias>";
    $(this.content).find('.criteria').each(function(index) {
        var inputs = this.getElementsByTagName('input');
        var select = this.getElementsByTagName('select');
        var name = inputs[0].value;
        var code = inputs[1].value;
        var type = select[0].value;

        // Check if all input as completed
        if(code!="" && name!="" && type!="") {
            xml += '<criteria code="'+code+'" name="'+name+'" type="'+type+'">';

            if(type == "enum") {
                for(var i=2; i<inputs.length;i+=2) {
                    var value = inputs[i].value;
                    var vcode = inputs[i+1].value;
                    if(value!="" && vcode!="")
                        xml += '<value code="'+vcode+'" name="'+value+'" />';
                }
            } else if(type == "int") {
                var min = inputs[2].value;
                var max = inputs[3].value;

                if(min!="" && max!="")
                    xml += '<range min="'+min+'" max="'+max+'" />';
                else if(min!="")
                    xml += '<range min="'+min+'" />';
                else if(max!="")
                    xml += '<range max="'+max+'" />';
            }
            xml += '</criteria>';
        }
    });
    
    xml += "</criterias>";
    return xml;
}

// Editor actions
criteriaseditor.prototype.init_editor_actions = function() {
    var me=this;
    if (kolekti.uid != '0') {
    if(this.can_save()) {
        var eltact=document.createElement('span');
        eltact.className="vieweritemaction";
        iconact=document.createElement('img');
        iconact.setAttribute('src','/_lib/kolekti/icons/icon-save-off.png');
        iconact.setAttribute('alt',i18n("[0083]Enregistrer"));
        iconact.setAttribute('title',i18n("[0083]Enregistrer"));
        eltact.appendChild(iconact);
        var save=document.createElement('span');
        save.className="viewershortnameaction disabled";
        save.setAttribute('title',i18n("[0083]Enregistrer"));
        save.textContent=i18n("[0083]Enregistrer");
        eltact.appendChild(save);
        var act = new Object();
        act.icon = iconact;
        act.elt = save;
        this.save_action_button=act;
        this.vieweractions.appendChild(eltact);
        eltact.addEventListener('click',function(e){me.do_save(e)},false);
    }
    kolekti.listen('editor-resourcemodified',function(arg){me.cb_modified(arg);return true;},this.context.id);
    kolekti.listen('quit-page',function(arg){return me.statesaved;},this.context.id);
    }
    this.statesaved=true;
}
