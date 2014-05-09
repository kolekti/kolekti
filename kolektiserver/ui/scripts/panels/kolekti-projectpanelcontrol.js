/*

     kOLEKTi : a structural documentation generator
     Copyright (C) 2007-2010 Stéphane Bonhomme (stephane@exselt.com)

     This program is free software: you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation, either version 3 of the License, or
     (at your option) any later version.

     This program is distributed in the hope that it will be useful,
     but WITHOUT ANY WARRANTY; without even the implied warranty of
     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
     GNU General Public License for more details.

     You should have received a copy of the GNU General Public License
     along with this program.  If not, see <http://www.gnu.org/licenses/>.

*/
/*
   Class for the kolekti panelcontrol component
*/
//author Guillaume Faucheur <guillaume@exselt.com>

function kolekti_projectpanelcontrol() {
    this.splitcontentleft=true;
    this.splitcontentright=true;
}

kolekti_projectpanelcontrol.prototype=new kolekti_panelcontrol;

kolekti_projectpanelcontrol.prototype.change_state=function(args) {
    var right = document.getElementById('splitcontentright');
    var left = document.getElementById('splitcontentleft');
    var isopen = this.isopen(args.target);

    if(this.isopen('splitcontentright'))
        right.removeAttribute('style');
    if(this.isopen('splitcontentleft'))
        left.removeAttribute('style');

    // Panel is open
    if(isopen) {
        this[args.target] = false;
        this.close(args.target);
    } else {
        this[args.target] = true;
        this.open(args.target);
    }

    if(this.splitcontentleft && this.splitcontentright) {
        right.removeAttribute("style");    //Default panel width + sidebar width
    } else if(this.splitcontentleft && !this.splitcontentright) {
        left.style.right = "0";
        left.style.width = "auto";
    } else if(!this.splitcontentleft && this.splitcontentright) {
        right.style.left = "0";
        right.style.width = "auto";
    } else {
        this.close("splitcontentright");
        this.close("splitcontentleft");
    }

    this.change_icon_state(args.id);
}
