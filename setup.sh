#Kacper Skelnik 291566
#Wojciech Tyczyński 291563
#!/bin/bash

python3 -m pip install --user virtualenv
python3 -m virtualenv -q envWeb 
source envWeb/bin/activate
envWeb/bin/pip install -r requirements.txt