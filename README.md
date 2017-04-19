# pymongo_basemodel

[![Travis](https://img.shields.io/travis/chrisantonellis/pymongo_basemodel.svg?style=flat-square)](https://travis-ci.org/chrisantonellis/pymongo_basemodel) [![Coveralls](https://img.shields.io/coveralls/chrisantonellis/pymongo_basemodel.svg?style=flat-square)](https://coveralls.io/github/chrisantonellis/pymongo_basemodel?branch=master)  

pymongo_basemodel ( **baemo** ) is a PyMongo ODM/ORM that implements the unit of work pattern 
and supports document referencing and dereferencing

# API

### ```DelimtedDict```
* ```ref```  
* ```get```
* ```has```
* ```spawn```
* ```clone```
* ```set```
* ```push```
* ```pull```
* ```unset```
* ```merge```
* ```update```
* ```collapse```

### ```Connection```
* ```get```
* ```set```

### ```Entity```
* ```Entity()```

### ```Entities```
* ```get```
* ```set```

### ```Model```
* ```set_target```
* ```get_target```
* ```get_id```
* ```find```
* ```ref```
* ```has```
* ```get```
* ```set```
* ```unset```
* ```unset_many```
* ```push```
* ```push_many```
* ```pull```
* ```pull_many```
* ```delete```
* ```reset```
* ```pre_insert_hook```
* ```post_insert_hook```
* ```pre_update_hook```
* ```post_update_hook```
* ```pre_delete_hook```
* ```post_delete_hook```

### ```Collection```
* ```set_target```
* ```get_target```
* ```get_targets```
* ```get_ids```
* ```find```
* ```ref```
* ```has```
* ```get```
* ```set```
* ```unset```
* ```unset_many```
* ```push```
* ```push_many```
* ```pull```
* ```pull_many```
* ```delete```
* ```reset```
* ```save```
* ```add```
* ```remove```
* ```pre_modify_hook```
* ```post_modify_hook```

### ```Projection```
* ```set```
* ```merge```
* ```update```
* ```flatten```

### ```Sort```
* ```set```
* ```merge```
* ```update```
* ```flatten```

### ```References```
* ( no public methods )
