#Kacper Skelnik 291566
#Wojciech Tyczyński 291563
#!/bin/bash

read -p "Enter server IP : " server
if [[ $server =~ ^[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
  	export server
	source envWeb/bin/activate
	export FLASK_APP=app
	flask run
else
  echo "Invalid IP"
fi
