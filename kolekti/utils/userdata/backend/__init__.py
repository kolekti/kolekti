# -*- coding: utf-8 -*-
#
# load the right module in function of configuration
# here we only load sqlite module
#     kOLEKTi : a structural documentation generator
#     Copyright (C) 2007-2010 Stéphane Bonhomme (stephane@exselt.com)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.


import pickle

#from kolekti.mvc.models.sql.models import Userdata

class backend(object):
    def __init__(self,namespace,http):
        if http is None:
            from kolekti.utils.backends.sqlalchemybackend import SQLAlchemyBackend
            self.sql = SQLAlchemyBackend()
            self.sql.connect()
        else:
            self.sql = http.dbbackend

    def delete(self,namespace,key):
        Userdata = self.sql.get_model('Userdata')
        dele = self.sql.select(Userdata, "namespace='%s' and keyid='%s'" %(namespace, key))[0]
        self.sql.delete(dele[0])

    def set(self,namespace,key,record):
        Userdata = self.sql.get_model('Userdata')
        try:
            ins = Userdata(namespace, key, record.get('type'), pickle.dumps(record.get('value')))
            self.sql.insert(ins)
        except:
            self.sql.rollback()
            set = self.sql.select(Userdata, "namespace='%s' and keyid='%s'" %(namespace, key))[0]
            set.type = record.get('type')
            set.record = pickle.dumps(record.get('value'))

    def get(self,namespace,key):
        type=record=None
        try:
            Userdata = self.sql.get_model('Userdata')
            res = self.sql.select(Userdata, "namespace='%s' and keyid='%s'" %(namespace, key))[0]
            type = res.type
            record = pickle.loads(str(res.record))
        except:
            pass
        return(type,record)

