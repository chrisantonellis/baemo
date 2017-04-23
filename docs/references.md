
```
{
  "vehicles": { ............ Reference name

    "entity": "vehicle", ... Entity name

    "type": "one_to_one" ... Type of relationship

    "source": "" ........... Name of attribute that contains 
                             reference(s). If undefined, reference name 
                             is used. Optional

    "destination": "" ...... Name of attribute that will 
                             contain resolved reference(s). If undefined, 
                             reference name is used. Optional

    "foreign_key": "" ...... Name of attribute on foreign model 
                             that contains reference data. If undefined, 
                             id_attribute of entity model is used. Optional
  }
}
```