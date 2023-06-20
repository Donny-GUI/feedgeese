import os

path = os.path.join(os.getcwd(), "index.css")

with open(path, 'r') as rfile:
    contents = rfile.read()
    
lines = contents.split("\n")
keyframes = []
keydatas = []
items = []
itemdatas = []
dataswitch = False
keyswitch = False

current_item = ""
current_key = ""

for line in lines:
    
    if line.startswith("."):
        items.append(line[:-1])
        dataswitch = True
        if current_item != "":
            itemdatas.append(current_item)
            current_item = ""
        continue
    elif line == "}":
        dataswitch = False
        keyswitch = False
        continue
    elif line.startswith("@keyframes"):
        keyframes.append(line[:-1])
        dataswitch = False
        keyswitch = True
        if current_key != "":
            keydatas.append(current_key)
            current_key = ""
        continue
    elif dataswitch:
        current_item+=line
        current_item+="\n"
        continue
    elif keyswitch:
        current_key+=line
        current_key+="\n"
        

for key in keydatas:
    lines = reversed(key.split("\n"))
    for line in lines:
        print(line)
    
