#!/bin/bash
mongod --quiet --logpath=/dev/null &
green test -r
