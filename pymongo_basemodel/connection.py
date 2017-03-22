
_connections = {}
_default_connection = None


def add_connection(db, connection):
  global _connections, _default_connection

  _connections[db] = connection
  if not _default_connection:
    set_default_connection(db)

def set_default_connection(db):
  global _connections, _default_connection
  
  _default_connection = _connections[db]

def get_connection(db=None, collection=None):
  global _connections, _default_connection  

  if db:
    connection = _connections[db]
  else:
    connection = _default_connection

  if collection:
    connection = connection[collection]

  return connection
