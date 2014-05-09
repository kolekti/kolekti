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
   Class for the kolekti panelcontrol component
*/
//author Guillaume Faucheur <guillaume@exselt.com>

function kolekti_panelcontrol() { }

kolekti_panelcontrol.prototype.initevent= function() {
    var me=this;
    kolekti.listen('panelcontrol-change',function(args){me.change_state(args);return true;},null);    
}

// Override this method
kolekti_panelcontrol.prototype.change_state=function(args) {
}

// Return state of panel
kolekti_panelcontrol.prototype.isopen=function(target) {
    return !(document.getElementById(target).style.display == "none");
}

// open panel
kolekti_panelcontrol.prototype.open=function(target) {
    document.getElementById(target).style.display = "block";
}

// close panel
kolekti_panelcontrol.prototype.close=function(target) {
    document.getElementById(target).style.display = "none";
}

//Change picture
kolekti_panelcontrol.prototype.change_icon_state=function(id) {
    var pelem = document.getElementById(id);
    var span = pelem.getElementsByTagName("span");
    
    if(span[0].className == "activepanel") {
        span[0].className = "";
        span[1].className = "activepanel";
    } else {
        span[0].className = "activepanel";
        span[1].className = "";
    }
}
