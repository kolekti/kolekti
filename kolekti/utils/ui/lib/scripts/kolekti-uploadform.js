/*
 *    kOLEKTi : a structural documentation generator
 *    Copyright (C) 2007-2010 Stéphane Bonhomme (stephane@exselt.com)
 *
 *   This program is free software: you can redistribute it and/or modify
 *   it under the terms of the GNU Affero General Public License as
 *   published by the Free Software Foundation, either version 3 of the
 *   License, or any later version.
 *
 *   This program is distributed in the hope that it will be useful,
 *   but WITHOUT ANY WARRANTY; without even the implied warranty of
 *   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 *   GNU Affero General Public License for more details.
 *
 *   You should have received a copy of the GNU Affero General Public License
 *   along with this program.  If not, see <http://www.gnu.org/licenses/>.
*/


/*
   Class for the kolekti upload component
*/
//author Guillaume Faucheur <guillaume@exselt.com>

function kolekti_uploadform(url, id) {
    this.url = url;
    this.id = id;
    this.multiple = 0;
}

// init events method
kolekti_uploadform.prototype.initevent= function() {
    var me = this;
    window.addEventListener('load', function(arg) {return me.load();}, null);
}

// After load check if multiple file form
kolekti_uploadform.prototype.load= function() {
    var me = this;
    if(this.multiple == 1)
        this.add_btnfile();
    this.set_action_url();
}

// Add buttton to add new file
kolekti_uploadform.prototype.add_btnfile= function() {
    var me = this;
    var form = document.getElementById(this.id);
    var p = document.createElement("p");
    p.className="btn_addfile";
    var btn_add = document.createElement('button');
    btn_add.textContent = i18n("[0310]Ajouter un fichier");
    p.appendChild(btn_add);
    form.parentNode.insertBefore(p, form.nextSibling);

    btn_add.addEventListener('click',function(e){me.add_file()},false);
}

// Copy file node
kolekti_uploadform.prototype.add_file= function(btn_add) {
    var files = document.getElementById('filelines');
    var child = files.firstChild;
    while(child) {
        if(child.nodeType == '1' && child.nodeName == 'P')
            break;
        child = child.nextSibling;
    }
    var newfile = child.cloneNode(true);
    files.appendChild(newfile);
}

// Set form action url
kolekti_uploadform.prototype.set_action_url = function() {
    var form = document.getElementById(this.id);
    form.action = this.url+"?uploadform=1";
}
