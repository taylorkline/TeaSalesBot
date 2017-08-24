#!/bin/bash

jsonschema -i vendors.json vendors.schema.json && python3.6 bot_tests.py
