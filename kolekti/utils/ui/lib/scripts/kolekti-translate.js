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
   Class for the kolekti sidebar component
*/
//author Stéphane Bonhomme <stephane@exselt.com>

function kolekti_translate(id) {
    this.id = id;
}

kolekti_translate.prototype.submit = function(url) {
    var form = document.getElementById(this.id);
    var inputs = form.getElementsByTagName('input');
    var conn = new ajax(url);
    for(var i=0; i<inputs.length; i++) {
        var inp = inputs[i];
        conn.setParameter()
    //conn.send('POST');
}
