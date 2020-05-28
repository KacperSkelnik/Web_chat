#!/bin/bash

read -p "Enter IP name: " ip_name
export ip_name
source envWeb/bin/activate
python3 server.py