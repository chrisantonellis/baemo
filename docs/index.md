
## what does baemo actually do

references is a big part, it can resolve references and they

```
"thing": "thing"
```

# pymongo_basemodel

pymongo_basemodel ( **baemo** ) is a PyMongo ODM/ORM that implements the unit of work pattern
and supports document referencing and dereferencing

## Purpose

MongoDB does not provide complex reference resolution out of the box
Projection is extended to be
Multiple representations of the same data is a requirement of current web apps,
and for security reasons it is sometimes required to omit rather than simply
hide certain pieces of data.

A document is represented as a ```Model``` when loaded from the db, and a group
of documents is represented as a ```Collection```.






NoSQL lets you have schemaless documents and embed nested data in documents, but
doesn't provide mechanisms for referense resolution out of the box, ouch!

Baemo addresses this by ```Entity```s and ```References```s

baemo addresses this by extending the MongoDB ```Projection``` concept to allow
for resolving references and reshaping db data at the same time.

Through registering ```Entity``` sets and defining ```Reference``` definitions,
you can define complex circular relationships without worrying about circular
dependency. Using expanded ```Projections``` you can then request exactly which
references should be resolved and which fields should be returned. I guess its
kinda like GraphQL without all the facebook bullshit?




nosql databases offer flexibility, but this is not taken advantage of by current
orm implementations which seem to borrow concepts from SQL db ORMs

baemo aims to build on the powerful ```Projection``` concept introducted by MongoDB,
extending it to allow for
specifically, allowing for re-use of otherwise brittle concepts





current mongodb orm/odm implementations do not fully take advantage of the strengths
of mongodb which are (in the author's opinion) 1. schemaless documents that allow for
changing document structure in the db 2.
