
from ruamel.yaml import YAML
from collections import OrderedDict
from ruamel.yaml.scalarstring import PreservedScalarString
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import os
from firebase_admin import firestore, credentials, _apps, initialize_app
import unicodedata

path_cwd = os.getcwd()
cred_path = os.path.join(path_cwd, "service account\knowledgebase.json")
        
if not _apps:
    cred = credentials.Certificate(cred_path)
    initialize_app(cred)        
db = firestore.client()

def addtoNLU(data,collect,name,ty): #add data into the nlu

    doc_ref = db.collection(collect)
    getdoc=[]
    id=[]
    docs=doc_ref.get()
    for doc in docs:
        id.append(doc.id)
        getdoc.append(doc.to_dict())
    #print(getdoc[0]["test"])
    #print(len(getdoc))

    for i in range(len(getdoc)):
        #print(getdoc[i][name])
        #print(id[i])
        st=""
        for na in getdoc[i][name]:
            st=st+"- "+na+"\n"

        st=st.replace("’", "'").replace("“", '"').replace("”", '"')
        od={ty: id[i],"examples": PreservedScalarString(st)}
        data.append(od)

def lookSymp(data):
    doc_ref = db.collection("Symptoms")
    id=[]
    docs=doc_ref.get()
    st=""
    for doc in docs:
        st=st+"- "+doc.id+"\n"
    st=st.replace("’", "'").replace("“", '"').replace("”", '"')
    od={"lookup":"symptom" ,"examples": PreservedScalarString(st)}
    data.append(od)

yaml = YAML()
yaml.preserve_quotes = True  # Keeps quotes around strings
yaml.indent(mapping=2, sequence=4, offset=1)
yaml.default_flow_style = False


#with open('data/nlu.yml','r') as f:
#    data=yaml.load(f)
data=[]
addtoNLU(data,"regex","test","regex")
addtoNLU(data,"intent","test","intent")
addtoNLU(data,"lookup","test","lookup")
lookSymp(data)
addtoNLU(data,"Symptoms",'Related','synonym')

dic={
    "version":"3.1",
    "nlu": data
}
#print(data)
#print(type(data))
#data['nlu']#.append(od)#+", ordereddict([('synonym', 'pain'), ('examples', '- hurts\n- painful\n- cramps')])]"

with open('data/nlu.yml', 'w',encoding="utf-8") as outfile:
    yaml.dump(dic, outfile)