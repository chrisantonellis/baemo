# Dot Notation Syntax

pymongo_basemodel uses **dot notation syntax** to access the fields of embedded 
documents. Using dot notation syntax strings makes it possible to target 
nested data for access and modification.  

#### Getting & Setting Attributes

Dot notation syntax can be used when getting and setting attributes to access 
nested data.

```python
from pymongo_basemodel.core import Model
model = Model()

# set nested data
model.set("key1.key2.key3", "nested_data")

# value "nested_data" can be accessed using dot notation syntax
print(model.get("key1.key2.key3"))
```
```python
>>> "nested_data"
```
#### Update Queries

Dot notation syntax is used in MongoDB update query syntax to allow for 
updating specific fields in a document without overwriting adjacent fields. 
pymongo_basemodel will flatten cached model updates into dot notation syntax 
while taking into consideration ```$each``` and ```$in``` operators when 
writing updates to the database.

```python
from pymongo_basemodel.core import Model
model = Model()

# set nested data
model.set("key1.key2.key3", "nested_data")

# print flattened model.updates
print(model.flatten_updates())
```
```python
>>> {
>>>   "$set": {
>>>     "key1.key2.key3": "nested_data"
>>>   }
>>> }
```
