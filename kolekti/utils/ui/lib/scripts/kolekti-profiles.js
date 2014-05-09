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


kolekti_obj.prototype.get_profile_value=function(key) {
    var conn=new ajaxdav('/_profile'+key);
    props=conn.PROPFIND([{ns:'kolekti:profile',propname:'profilevalue'}],0);
}

kolekti_obj.prototype.set_profile_value=function(key,value) {
    var conn=new ajaxdav('/_profile'+key);
    props=conn.PROPPATCH([{ns:'kolekti:profile',propname:'profilevalue',propval:value}],[]);
}

kolekti_obj.prototype.del_profile_value=function(key) {
    var conn=new ajaxdav('/_profile'+key);
    props=conn.PROPPATCH([],[{ns:'kolekti:profile',propname:'profilevalue',propval:value}]);
}
