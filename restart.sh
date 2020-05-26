#!/bin/bash

kill $(cat app.pid)
flask run