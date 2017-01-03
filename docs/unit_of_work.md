* record change
* simple
* more complicated
* intelligent for push, pull
* can write to nested models / collections



# Record Change
caches model changes to be persisted to db on save call to achieve unit of
work patten

methods used:
set
push
pull
unset

changes get processed by record_change and set in changed array attribute
flatten changed get in pymongo nested data syntaxs






The unit of work pattern is acheived by caching model attribute changes in 
MongoDB operator syntax.

##### The Unit of Work pattern is achieved by caching model changes
```python
from pymongo_basemodel.core import Model

model = Model()

model.set("key", "value")
model.set("deep.nested.key", "value")

model.pull("things", "value_1")
model.pull("things", "value_2")

print(model.changed)

>>> {
>>>   "$set": {
>>>     "key": "value"
>>>     "deep.nested.key": "value"
>>>   },
>>>   "$pull": {
>>>     "things": {
>>>       "$in": [ "value_1", "value_2" ]
>>>     }
>>>   }
>>> }

model.save()
```
##### model changes are cached intelligently to keep MongoDB query valid
```
complicated setup
model.set()
model.push()
model.push()
```




* model
  * save, changed
* collection
  * save, bulk write