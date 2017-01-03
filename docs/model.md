# Model
```Model``` is an abstraction of a MongoDB document, and is the core component 
of pymongo_basemodel. It is an attribute container that maintains the state of 
a document as well as a cache of attribute updates. Attribute updates are 
translated into MongoDB operator syntax and are only written to the database 
when ```model.save()``` is called.

## Defining Models

* pymongo collection
* default_find_projection
* default_get_projection
* relationships

## Creating Models
* Create a ```Model```
  ```python
  from pymongo_basemodel.core import Model

  model = Model()
  ```

* Create a ```Model``` and set ```model.target```  
  ```model.target``` determines the target document for MongoDB update and delete 
  operations.
  ```python
  from pymongo_basemodel.core import Model

  model = Model({ "last_name": "Antonellis" })

  print(model.target)
  ```
  ```python
  >>> { "last_name": "Antonellis" }
  ```
  If target is not of type ```dict``` the key of target is set 
  to ```model.id_attribute```
  ```python
  from pymongo_basemodel.core import Model
  from bson.objectid import ObjectId

  model = Model(ObjectId('085en78886a3s19644e0vdc8'))

  print(model.target)
  ```
  ```python
  >>> { "_id": ObjectId('085en78886a3s19644e0vdc8') }
  ```

### Modifying Attributes
* mention + link to dot notation syntax
* set, string, dict
* push, link to push many in api page
* push many
* pull
* pull many
* 

### Unit of Work
* create
  * default projection
* target
* find
* attribute access
  * apply projection
* attribute modification
* save
  * insert
  * update
    * update without find
  * delete