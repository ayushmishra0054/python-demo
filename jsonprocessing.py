import json,requests
#deserialise
with open('/home/ayush/Documents/Python-Demo/todos.json') as f:
    data=json.load(f)
data2=json.dumps(data,indent=2)

def serialise(data2):
    json.dump(data2, '/home/ayush/Documents/Python-Demo/todos.json')
def search(param,field):
    pass
