# pymongo_basemodel

[![Travis](https://img.shields.io/travis/chrisantonellis/pymongo_basemodel.svg?style=flat-square)](https://travis-ci.org/chrisantonellis/pymongo_basemodel) [![Coveralls](https://img.shields.io/coveralls/chrisantonellis/pymongo_basemodel.svg?style=flat-square)](https://coveralls.io/github/chrisantonellis/pymongo_basemodel?branch=master)  

pymongo_basemodel ( **baemo** ) is a PyMongo ODM/ORM that implements the unit of work pattern 
and supports document referencing and dereferencing

## Caching Updates
Create a model
```python
from pymongo_basemodel.core import Model

model = Model()
```
Set data on the model
```python
model.set("key", "value")
model.set("deep.nested.key", "value")
model.push_many("things", [ "value_1", "value_2" ])
```
Examine cached model updates
```python
print(model.updates)
```
```python
{
  "$set": {
    "key": "value"
    "deep": {
      "nested": {
        "key": "value"
    }
  },
  "$push": {
    "key": {
      "$each": [ "value_1", "value_2" ]
    }
  }
}
``` 
Updates send to db on ```save()```
```python
model.save()
```
