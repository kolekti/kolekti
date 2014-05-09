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
   Class for the kolekti svnrevision component
*/
//author Guillaume Faucheur <guillaume@exselt.com>

function kolekti_svnrevision(id) {
    this.id = id;
}

kolekti_svnrevision.prototype.initevent= function() {
    var me=this;
    kolekti.listen('svnrevision-change',function(args){me.change_svnrevision(args);return true;},null);
}

kolekti_svnrevision.prototype.change_svnrevision=function(args) {
    var rev;
    var svnrev = document.getElementById(this.id);
    var child = svnrev.firstChild;

    while(child) {
        if(child.className == "revision")
            rev = child;
        child = child.nextSibling;
    }

    var conn = new ajaxdav(args.url);
    var req = conn.PROPFIND([{'ns': 'kolekti', 'propname': 'revision'}]);
    
    if(req.result.status == "207") {
        var xpr=req.object;
        while (xpr.nextResponse()) {
            var prev=xpr.get_prop('kolekti','revision');
            if (prev.status=="200" && prev.content.firstChild)
                rev.textContent = prev.content.firstChild.textContent;
        }
    }
}