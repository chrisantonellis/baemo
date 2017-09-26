```
local_one
local_many
foreign_many
foreign_one

{
  "vehicles": { ................ reference name

    "entity": "vehicle", ....... entity name

    "type": "local_one" ........ type of reference

    "foreign_key": "" .......... name of attribute on foreign model that contains reference data
                                 OPTIONAL: if undefined, id_attribute of entity model is used
}
```