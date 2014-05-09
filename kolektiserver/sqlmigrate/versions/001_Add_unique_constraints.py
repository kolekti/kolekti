from sqlalchemy import Table, Column, MetaData, ForeignKey, Integer, String
from migrate import *
from migrate.changeset.constraint import UniqueConstraint

meta = MetaData()

projects = Table('projects', meta,
    Column('id', Integer, primary_key=True),
    Column('name', String(length=100)),
    Column('directory', String(length=50), unique=True),
    Column('description', String(length=300)),
    Column('lang', String(length=50)),
)

criterias = Table('criterias', meta,
    Column('id', Integer, primary_key=True),
    Column('pid', Integer, ForeignKey('projects.id')),
    Column('name', String(length=50)),
    Column('code', String(length=50)),
    Column('type', String(length=50)),
)

criteriavalues = Table('criteriavalues', meta,
    Column('id', Integer, primary_key=True),
    Column('criteria_id', Integer, ForeignKey('projects.id')),
    Column('value1', String(length=50)),
    Column('value2', String(length=50)),
)

def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind
    # migrate_engine to your metadata
    meta.bind = migrate_engine
    cons = UniqueConstraint('pid', 'code', name="criteria", table=criterias)
    cons.create()
    cons = UniqueConstraint('criteria_id', 'value1', 'value2', name="criteriavalue", table=criteriavalues)
    cons.create()

def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    meta.bind = migrate_engine
    cons = UniqueConstraint('pid', 'code', name="criteria", table=criterias)
    cons.drop()
    cons = UniqueConstraint('criteria_id', 'value1', 'value2', name="criteriavalue", table=criteriavalues)
    cons.drop()
