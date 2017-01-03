
# API Reference

## Attributes

### [target](#target)
```python
model.target
```
The database target by which a document will be looked up, updated, or deleted. 
This is independent from [id_attribute](#model.id_attribute) in that a model 
can be found by attributes other than its id_attribute.

| Type | Default | 
| :--: | :------ |
| ```dict``` | ```None``` |

### target
```python
model.target
```

### attributes
```python
model.attributes
```
### relationships
### default_attributes
### default_find_projection
### default_get_projection

### _original
```python
model.original
```

### _changed
### _delete_flag

## Methods

### [Model()](#Model)  
```python
pymongo_basemodel.core.Model(target=None)
```
Creates a new instance of ```pymongo_basemodel.core.Model```.  
##### kwargs
| Name | Type | Default | Description | 
| :--- | :--: | :-----: | :---------- |
| **target** | ```str``` | ```None``` | if set on instantiation, passed to ``` self.set_target()``` |



### [generate_id()](#generate_id)
```python
Model.generate_id()
```
Classmethod. Generates and returns a unique ID.  



### [set_target()](#set_target)
```python
model.set_target(target)
```
Sets ```model.target``` to target argument.  
If target is a ```str```, ```model.target``` is set to ```{ model.id_attribute: target }```
##### kwargs
| Name       | Type   | Default    | Description | 
| :--------- | :----- | :--------- | :---------- |
| **target** | string | ```None``` | description |



### [get_target](#get_target)
```python
model.get_target(target)
```
<br />

##### find(projection = None, merge_with_default = False)
###### kwargs
| Name       | Type   | Default    | Description | 
| :--------- | :----- | :--------- | :---------- |
| **target** | string | ```None``` | description |
---

##### get(key = None, reference = False, projection = None, merge_with_default = False, haystack = None, setup = False)
###### kwargs
| Name       | Type   | Default    | Description | 
| :--------- | :----- | :--------- | :---------- |
| **target** | string | ```None``` | description |

##### set()

##### push()

##### push_many()

##### pull()

##### pull_many()

##### unset()

##### unset_many()


##### save()

##### delete()

##### reset()


pre_insert_hook
post_insert_hook
pre_find_hook
post_find_hook
pre_update_hook
post_update_hook
pre_delete_hok
post_delete_hook

