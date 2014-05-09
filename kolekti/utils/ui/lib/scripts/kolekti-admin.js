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
   Class for the kolekti admin forms : verify fields value before posting
*/

//author Stéphane Bonhomme <stephane@exselt.com>

function kolekti_admin() {
}

kolekti_admin.prototype.verify=function() {
	var inputs= document.getElementsByTagName("input");
	var mdp = "";
	var noError = true;
	
	for(var i=0; i<inputs.length; i++) {
		var input = inputs[i];
		if(input.parentNode.className == "required") {			
			if(input.value == "") {
				input.setAttribute("style", "background-color: red;");
				noError =  false;
			} else {
				input.removeAttribute("style");
			}
		}
		
		if(input.getAttribute("type") == "password") {
			if(mdp == "") {
				mdp=input.value;
			}
			else if(input.value != mdp) {
				input.setAttribute("style", "background-color: red;");
				noError = false;
			}
			else {
				input.removeAttribute("style");
			}
		}		
	}
	
	return noError;
}

kolekti_admin.prototype.deletedata=function(url) {
	var conn = new ajax(url);
	res = conn.post();
}

var kadmin = new kolekti_admin();

