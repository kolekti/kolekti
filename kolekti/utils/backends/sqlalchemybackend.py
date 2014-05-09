# -*- coding: utf-8 -*-
#
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

"""
    SQLAlchemy IO
"""

__author__  = '''Guillaume Faucheur <guillaume@exselt.com>'''

import os
import sys
import imp
import migrate.versioning.api

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool
from sqlalchemy import MetaData

from kolekti.kolekticonf import conf

class SQLAlchemyBackend(object):
    __sqlurl = ""
    __engine = None
    __session = None
    __models=[]
    
    @property
    def session(self):
        return self.__session
    
    def set_session(self):
        Session = sessionmaker(self.__engine)
        self.__session = Session()
    
    def rollback(self):
        return self.__session.rollback()

    def close(self):
        self.__session.close()

    def commit(self):
        return self.__session.commit()

    def create_tables(self):
        for m in self.__models:
            metadata = getattr(m, 'Base').metadata
            self.__create_tables(metadata)

    def connect(self):
        # Connection of DB and load tables
        if self.__engine is None:
            self.__load_db()

    def get_model(self,modelname):
        for m in self.__models:
            try:
                model=getattr(m,modelname)
                return model
            except:
                pass
        raise 
        
    def __load_db(self):
        dbconf = (conf.get('db_type').lower(),
                  conf.get('db_login'),
                  conf.get('db_passwd'),
                  conf.get('db_host'),
                  conf.get('db_base'))
        self.__sqlurl = '%s://%s:%s@%s/%s'%dbconf
        self.__engine = create_engine(self.__sqlurl, encoding='utf-8', poolclass=NullPool)
        # Load module
        self.__load_sqlmodules()
        for m in self.__models:
            metadata = getattr(m, 'Base').metadata
            metadata.bind = self.__engine
            m.meta = metadata
            # Create new session
            self.set_session()

    def __load_sqlmodules(self):
        self.__models=[]
        for dbmodel in (conf.get('db_fmk_model'), conf.get('db_app_model')): 
            # try load module
            try:
                module=sys.modules[dbmodel]
                self.__models.append(module)
            except KeyError:
                # import module name
                fp = None
                try:
                    fp, pathname, description = imp.find_module(dbmodel,conf.sqlpathlist)
                    module = imp.load_module(dbmodel, fp, pathname, description)
                    self.__models.append(module)
                except:
                    pass
                finally:
                    # Since we may exit via an exception, close fp explicitly.
                    if fp:
                        fp.close()

    def __create_tables(self, metadata):
        createtable = False
        connection = self.__engine.connect()
        connection.detach()
        for table in metadata.tables.itervalues():
            try:
                connection.create(table)
                createtable = True
            except:
                pass
        connection.close()
        if createtable:
            self.__set_last_version_control()

    def select(self, obj, filter=None, order_by=None):
        if filter is None:
            res = self.__session.query(obj)
        else:
            res = self.__session.query(obj).filter(filter)

        if order_by:
            res = res.order_by(order_by)
        return res.all()

    def insert(self, objects, autocommit=True):
        if type(objects) == list:
            self.__session.add_all(objects)
        else:
            self.__session.add(objects)
        if autocommit:
            self.__session.commit()

    def delete(self, objects, autocommit=True):
        if type(objects) == list:
            for obj in objects:
                self.__session.delete(obj)
        else:
            self.__session.delete(objects)
        if autocommit:
            self.__session.commit()

    def upgrade_models(self):
        self.create_tables()

        if not self.is_update_models():
            repository = os.path.join(conf.get('appdir'), "sqlmigrate")
            migrate.versioning.api.upgrade(self.__sqlurl, repository)

    def is_update_models(self):
        repository = os.path.join(conf.get('appdir'), "sqlmigrate")
        try:
            curversion = migrate.versioning.api.db_version(self.__sqlurl, repository)
        except:
            migrate.versioning.api.version_control(self.__sqlurl, repository)
            curversion = 0
        lastversion = migrate.versioning.api.version(repository)
        return curversion == lastversion

    def __set_last_version_control(self):
        repository = os.path.join(conf.get('appdir'), "sqlmigrate")
        curversion = migrate.versioning.api.version(repository)
        migrate.versioning.api.version_control(self.__sqlurl, repository, version=curversion)
