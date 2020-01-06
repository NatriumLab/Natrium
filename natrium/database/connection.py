from pony import orm
from conf import config

db = orm.Database()
db.bind(**config['connection'])

from . import models
db.generate_mapping(create_tables=True)