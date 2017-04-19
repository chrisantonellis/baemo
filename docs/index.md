# pymongo_basemodel

pymongo_basemodel ( **baemo** ) is a PyMongo ODM/ORM that implements the unit of work pattern 
and supports document referencing and dereferencing 

## Cached Updates
Create a model
```python
from pymongo_basemodel.model import Model

model = Model()
```
Set data on the model
```python
model.set("key", "value")
model.pull("deep.nested.key", "value")
```
Examine cached model updates
```python
print(model.updates)
```
```php
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
Updates sent to db on ```save()```
```python
model.save()
```
