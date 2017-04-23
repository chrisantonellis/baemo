# pymongo_basemodel

# API

* [Connections](#connections)
  * [Connections.set()](#connections.set)
  * [Connections.get()](#connections.get)
* [Entity](#entity)
* [Entities](#entities)

<a name="connections"></a>
## class **Connections**
A simple PyMongo connection manager.  
Add connections to the cache using `Connections.set()` and retrieve them using `Connections.get()`.

* [Connections.set()](#connections.set)
* [Connections.get()](#connections.get)

### Methods

<a name="connections.set"></a>
* #### Connections.set(*name*, *connection*, default=*False*)
  Adds a PyMongo database connection to the cache at key `name`.  
  The first connection set will automatically become the default connection.  
  ```python
  connection = MongoClient()["app"]
  Connections.set("app", connection)
  ```
  The default connection can by manually set by calling `set` with the `default` keyword argument set to `True`.
  ```python
  Connections.set("app", connection, default=True)
  ```
<a name="connections.get"></a>
* #### Connections.get(name=None, collection=None)
  Returns PyMongo connection `name` from the cache and resolves reference to a PyMongo collection using string `collection`. If key `name` is not set in cache `ConnectionNotSet` is raised.  
  ```python
  users_collection = Connections.get("app", "users")
  users_collection.find_one(...)
  ```
  If `collection` is `None` the MongoDB connection is returned directly.  
  ```python
  app_database = Connections.get("app")
  ```
  If `collection` is not `None`, a reference to the PyMongo collection is obtained by performing `connection[collection]`.  
  ```python
  users_collection = Connections.get("app", "users")
  ```
  If `name` is `None` the default connection is returned.  
  If no default connection is set `ConnectionNotSet` is raised.  
  ```python
  products_collection = Connections.get(collection="products")
  ```

<a name="entity"></a>
## class **Entity**
A metaclass that constructs and returns `Model` and `Collection` classes using passed options and registers them with the [`Entities`](#entities) cache.
```python
User, Users = Entity("User", {
  # model options
  "connection": "app",
  "collection": "users"
}, {
  # collection options
  "limit": 50
})
```

* [Entity()](#entity)

<a name="entity"></a>
* #### Entity(name, model_options=None, collection_options=None)
  Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.

<a name="entities"></a>
## class **Entities**

* #### get()

### ```Entities```
* ```get```
* ```set```

### ```Model```
* ```set_target```
* ```get_target```
* ```get_id```
* ```find```
* ```ref```
* ```has```
* ```get```
* ```set```
* ```unset```
* ```unset_many```
* ```push```
* ```push_many```
* ```pull```
* ```pull_many```
* ```delete```
* ```reset```
* ```pre_insert_hook```
* ```post_insert_hook```
* ```pre_update_hook```
* ```post_update_hook```
* ```pre_delete_hook```
* ```post_delete_hook```

### ```Collection```
* ```set_target```
* ```get_target```
* ```get_targets```
* ```get_ids```
* ```find```
* ```ref```
* ```has```
* ```get```
* ```set```
* ```unset```
* ```unset_many```
* ```push```
* ```push_many```
* ```pull```
* ```pull_many```
* ```delete```
* ```reset```
* ```save```
* ```add```
* ```remove```
* ```pre_modify_hook```
* ```post_modify_hook```

### ```Projection```

### ```Sort```

### ```References```

# Glossary

1. <a name="delimited_string">**Delimited String**</a>  
  Delimited strings are strings that contain different fields separated by a single delimiter character. Example: ```user.status.active```






## *class* **DelimitedStr**

Emulates a string and handles **[delimited strings](#delimited_string)**.  
Allows for accessing and modifying parts of the delimited string by  index or slice.

* ### DelimitedStr(string=*None*)
  Creates a new instance of `DelimitedStr` using the string type  `string`. If `string` is `None` the value `""` is used.
  ```python
  str = DelimitedString("key1.key2.key3")
  ```
* ### \_\_getitem\_\_(index)
  Returns the value at `index`.
  ```python
  str = DelimitedString("key1.key2.key3")
  print(str[1])
  ```
  ```python
  "key2"
  ```
  
  Keys can also be accessed by slice. Keys accessed by slice will be returned joined by the `delimiter` attribute.
  ```python
  str = DelimitedString("key1.key2.key3")
  print(str[1:])
  ```
  ```python
  "key2.key3""
  ```

* ### \_\_contains\_\_(key)
  Tests for membership of `key` in `keys` attribute.
  ```python
  str = DelimitedString("key1.key2.key3")
  print("key2" in str)
  ```
  ```python
  True
  ```




## *class* **DelimitedDict**
Description of what this does

```
simple example
```

* ### DelimitedDict(data=None)
  Creates a new instance of `DelimitedDict`

* ### ref(key=*None*)
  Returns a reference to the value of `key` in `self.__dict__`.  
  If `key` is `None` a reference to all attributes is returned.

* ### get(key=*None*)
  Returns a copy of the value of `key` in `self.__dict__`.  
  If `key` is `None` a copy of all attributes is returned.

* ### has(key=*None*)


### spawn(key=*None*)

### clone(key=*None*)

### set(key, value)

### push(key, value)

### pull(key, value)

### unset(key)

### merge()

### update()

### collapse()
