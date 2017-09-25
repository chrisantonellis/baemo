
local_to_many
local_many
local_one

foreign_many
foreign_one

{
  "vehicles": { ................ reference name

    "entity": "vehicle", ....... entity name

    "type": "local_one" ........ type of reference

    "foreign_key": "" .......... name of attribute on foreign model that contains reference data
                                 OPTIONAL: if undefined, id_attribute of entity model is used

    "delete_policy": "deny" .... policy for handling reference on deletion
                                 OPTIONAL: if undefined, "nothing" is used
  }
}

when I am deleted, what happens to this reference if set

"ignore"
"deny"
"remove"
"cascade"


dependents are expressed as dict showing field that contains reference
data and specifies delete rule using an integer

self.dependents = {
    "units": 2
}

-1 - deny deletion
    raise exception if references
0 - do nothing (default)
    what it sounds like
1 - remove
    UNSET or PULL reference from dependent objects
2 - cascade
    delete dependent objects first