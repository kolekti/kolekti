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


kolekti_obj.prototype.get_session_value=function(key) {
    var conn = new ajaxdav('/_session'+key);
    var props = conn.PROPFIND([{ns:'kolekti:session',propname:'sessionvalue'}],0);
    var xpr=props.object;
    xpr.nextResponse();
    return xpr.get_prop('kolekti:session','sessionvalue');
}

kolekti_obj.prototype.set_session_value=function(key,value) {
    var conn = new ajaxdav('/_session'+key);
    var props = conn.PROPPATCH([{ns:'kolekti:session',propname:'sessionvalue',propval:value}],[]);
}

kolekti_obj.prototype.del_session_value=function(key) {
    var conn = new ajaxdav('/_session'+key);
    var props = conn.PROPPATCH([],[{ns:'kolekti:session',propname:'sessionvalue'}]);
}
