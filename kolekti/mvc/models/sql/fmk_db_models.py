# -*- coding: utf-8 -*-

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



__author__ = "bonhomme"
__date__ = "$Jul 20, 2009 1:30:57 PM$"
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Table, Column, LargeBinary, Boolean, Integer, Unicode, MetaData, ForeignKey

Base = declarative_base()

# Users class
class Users(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    login = Column(Unicode(100), unique=True)
    password = Column(Unicode(100))
    firstname = Column(Unicode(100))
    lastname = Column(Unicode(100))
    email = Column(Unicode(100))
    organization = Column(Unicode(100))
    lang = Column(Unicode(4))
    timezone = Column(Unicode(100))
    is_active = Column(Boolean)
    is_admin = Column(Boolean)
    is_translator = Column(Boolean)

    def __init__(self, login, password, firstname='', lastname='', email='', organization='', lang='fr', timezone='GMT', is_active=False, is_admin=False, is_translator=False):
        self.login = unicode(login)
        self.password = unicode(password)
        self.firstname = unicode(firstname)
        self.lastname = unicode(lastname)
        self.email = unicode(email)
        self.organization = unicode(organization)
        self.lang = unicode(lang)
        self.timezone = unicode(timezone)
        self.is_active = is_active
        self.is_admin = is_admin
        self.is_translator = is_translator

    def __repr__(self):
        return "<Users('%s','%s','%s','%s','%s', '%s','%s', %d','%d','%d')>" % (self.login, self.firstname, self.lastname, self.email, self.organization, self.lang, self.timezone, self.is_active, self.is_admin, self.is_translator)

# Userdata class
class Userdata(Base):
    __tablename__ = 'userdata'

    namespace = Column(Unicode(100), primary_key=True)
    keyid = Column(Unicode(200), primary_key=True)
    type = Column(Integer)
    record = Column(LargeBinary)

    def __init__(self, namespace, keyid, type, record):
        self.namespace = unicode(namespace)
        self.keyid = unicode(keyid)
        self.type = type
        self.record = record

    def __repr__(self):
        return "<Userdata('%s','%s','%d','%s')>" % (self.namespace, self.keyid, self.type, self.record)

