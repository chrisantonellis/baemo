
{
  "vehicles": { ................ reference name

    "entity": "vehicle", ....... entity name

    "type": "one_to_one" ....... type of relationship

    "source": "" ............... name of attribute that contains reference(s)
                                 OPTIONAL: if undefined, reference name is used

    "destination": "" .......... name of attribute that will contain resolved reference(s)
                                 OPTIONAL: if undefined, reference name is used

    "foreign_key": "" .......... name of attribute on foreign model that contains reference data
                                 OPTIONAL: if undefined, id_attribute of entity model is used
  }
}
