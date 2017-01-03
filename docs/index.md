# pymongo_basemodel

pymongo_basemodel ( **baemo** ) is a PyMongo ODM/ORM that implements the unit of work pattern 
and supports document referencing and dereferencing.

## 🔮 Black Magic  
Make a model
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
Examine cached model changes
```python
print(model.changed)
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