# -*- coding: utf-8 -*-
#
#     kOLEKTi : a structural documentation generator
#     Copyright (C) 2007-2011 Stéphane Bonhomme (stephane@exselt.com)
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
from sqlalchemy import Column, Integer, Unicode, ForeignKey, UniqueConstraint

# db import should be retrieved from config there
from kolekti.mvc.models.sql.fmk_db_models import Users

Base = declarative_base()

# Projects class
class Projects(Base):
    __tablename__ = 'projects'

    id = Column(Integer, primary_key=True)
    name = Column(Unicode(100))
    directory = Column(Unicode(50), unique=True)
    description = Column(Unicode(300))
    lang = Column(Unicode(50))

    def __init__(self, name, directory, description='', lang='fr'):
        self.name = unicode(name)
        self.directory = unicode(directory)
        self.description = unicode(description)
        self.lang = unicode(lang)

    def __repr__(self):
        return "<Projects('%s','%s','%s','%s')>" %(self.name, self.directory, self.description, self.lang)

# ProjectUser class
class ProjectUser(Base):
    __tablename__ = 'projectuser'

    project_id = Column(Integer, ForeignKey(Projects.id), primary_key=True)
    user_id = Column(Integer, ForeignKey(Users.id), primary_key=True)

    def __init__(self, project_id, user_id):
        self.project_id = project_id
        self.user_id = user_id

    def __repr__(self):
        return "<ProjectUser(%d,%d)>" %(self.project_id, self.user_id)

# ProjectScripts class
class ProjectScripts(Base):
    __tablename__ = 'projectscripts'

    project_id = Column(Integer, ForeignKey(Projects.id), primary_key=True)
    script_id = Column(Unicode(20), primary_key=True)

    def __init__(self, project_id, script_id):
        self.project_id = project_id
        self.script_id = script_id

    def __repr__(self):
        return "<ProjectScripts(%d,'%s')>" %(self.project_id, self.script_id)

# Usecase class
class Usecase(Base):
    __tablename__ = 'usecase'

    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey(Projects.id), primary_key=True)
    resid = Column(Unicode(300))
    ref = Column(Unicode(300))
    version = Column(Integer)

    def __init__(self, project_id, resid, ref, version=0):
        self.project_id = project_id
        self.resid = unicode(resid)
        self.ref = unicode(ref)
        self.version = version

    def __repr__(self):
        return "<Usecase('%d', '%s','%s',%d)>" %(self.project_id, self.resid, self.ref, self.version)

# Criterias class
class Criterias(Base):
    __tablename__ = 'criterias'

    id = Column(Integer, primary_key=True)
    pid = Column(Integer, ForeignKey(Projects.id))
    name = Column(Unicode(50))
    code = Column(Unicode(50))
    type = Column(Unicode(20))

    __table_args__ = (UniqueConstraint(pid, code, name="criteria"), {})

    def __init__(self, pid, name, code, type):
        self.pid = pid
        self.name = unicode(name)
        self.code = unicode(code)
        self.type = unicode(type)

    def __repr__(self):
        return "<Criterias('%d','%s','%s','%s')>" %(self.pid, self.name, self.code, self.type)

# CriteriaValues class
class CriteriaValues(Base):
    __tablename__ = 'criteriavalues'

    id = Column(Integer, primary_key=True)
    criteria_id = Column(Integer, ForeignKey(Criterias.id))
    value1 = Column(Unicode(50))
    value2 = Column(Unicode(50))

    __table_args__ = (UniqueConstraint(criteria_id, value1, value2, name="criteriavalue"), {})

    def __init__(self, criteria_id, value1, value2):
        self.criteria_id = criteria_id
        self.value1 = unicode(value1)
        self.value2 = unicode(value2)

    def __repr__(self):
        return "<CriteriaValues(%d,'%s','%s')>" %(self.criteria_id, self.value1, self.value2)

# MasterFilter class
class MasterFilter(Base):
    __tablename__ = 'masterfilter'

    id = Column(Integer, primary_key=True)
    pid = Column(Integer, ForeignKey(Projects.id))
    value = Column(Unicode(200))

    __table_args__ = (UniqueConstraint(pid, value, name="criteria"), {})

    def __init__(self, pid, value):
        self.pid = pid
        self.value = unicode(value)

    def __repr__(self):
        return "<MasterFilter('%d','%s')>" %(self.pid, self.value)

# OrdersHistory class
class OrdersHistory(Base):
    __tablename__ = "ordershistory"

    pid = Column(Integer, ForeignKey(Projects.id), primary_key=True)
    resid = Column(Unicode(300), primary_key=True)
    uid = Column(Integer, ForeignKey(Users.id))
    time = Column(Unicode(50))

    def __init__(self, pid, resid, uid, time):
        self.pid = pid
        self.resid = unicode(resid)
        self.uid = uid
        self.time = time

    def __repr__(self):
        return "<OrdersHistory('%d','%s', '%d', '%s')>" %(self.pid, self.resid, self.uid, self.time)
    