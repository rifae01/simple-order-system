#!/bin/bash
curl -X POST -H "Content-Type: application/json" -d '{"name":"Burger","price":99}' http://127.0.0.1:5000/items
curl http://127.0.0.1:5000/items
