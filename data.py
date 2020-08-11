import xml.etree.cElementTree as ET
import pprint
import re
import codecs
import json
import audit

### Change filename accordingly 
FILE="BengaluruUrban.osm"

### RE to match problematic characters in street names
problemchars = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')

### CREATED array which shall serve as a key list for Created field in the node
CREATED = [ "version", "changeset", "timestamp", "user", "uid"]

           
### Function to store data into the field of node_cre
def feed_node(node_cre,field,element):
    if field in element.attrib:
        node_cre[field]=element.attrib[field]

### Function to retrieve the field. Which was earlier seperated by a colon
def get_field(raw_field):
	field=raw_field.split(':')
	return field[1]

### Function to assign value to the field f_name of amenity
def assign(field,f_name,amenity):
    if len(field)==0:
       	pass
    elif len(field)==1:
        amenity[f_name]=field[0]
    else:
        amenity[f_name]=field


### Function to create a node for the element
def shape_element(element):
    node = {}
    if element.tag == "node" or element.tag == "way" :  
        feed_node(node,"id",element)
        node["type"]=element.tag
        feed_node(node,"visible",element)
        
        created={}
        for f in CREATED:
            feed_node(created,f,element)
        node["created"]=created
        
        ### Formation of position from longitude and latitude
        if element.tag=="node" :
            pos=[]
            pos.append(float(element.attrib["lat"]))
            pos.append(float(element.attrib["lon"]))
            node["pos"]=pos

        if element.tag=="way":
            node_refs=[]
            for nd in element.iter("nd"):
                node_refs.append(nd.attrib["ref"])
            node["node_refs"]=node_refs
                
        
        ### Formation of address and amenity fields
        ### email, phone and website are subfields of amenity
        address={}
        amenity={} 
        email=[]
        phone=[]
        website=[]
        for tag in element.iter("tag"):
            if problemchars.search(tag.attrib["k"]):
                pass
            elif (tag.attrib["k"]).startswith('addr:') and (tag.attrib["k"]).count(':')==1:
                field=get_field(tag.attrib["k"])
                address['city']='Bengaluru'
                address['state']='Karnataka'
                address['Country']='India'
                if field=='street':
                    address[field] = audit.update_name(tag.attrib["v"],audit.mapping)
                elif field=='postcode':
                    address[field] = audit.update_code(tag.attrib["v"])
                elif field=='housenumber_1' or field=='housenumber' or field=='number':
                    address['house_num'] = tag.attrib["v"]
                else:
                    pass
            elif tag.attrib["k"]=="ref" and node["type"]=="node":
                node['exit_num']=tag.attrib["v"]
            elif tag.attrib["k"] in ["name","amenity","access","office","email","contact:email","phone_2","phone_3","phone_1","phone","phone:mobile","contact:phone_2","contact:phone","website_1","website","contact:website"]: 
                if tag.attrib["k"]=="name" :
                    amenity["name"]=tag.attrib["v"]
                elif tag.attrib["k"]=="office":
                    amenity["office"]=tag.attrib["v"]
                elif tag.attrib["k"]=="amenity":
                    amenity["type"]=tag.attrib["v"]
                elif tag.attrib["k"]=="access":
                    amenity["access"]=tag.attrib["v"]
                elif tag.attrib["k"] in ["email","contact:email"]:
                    email.append(tag.attrib["v"])
                elif tag.attrib["k"] in ["phone_2","phone_3","phone_1","phone","phone:mobile","contact:phone_2","contact:phone"]:
                    phone.append(tag.attrib["v"])
                elif tag.attrib["k"] in ["website_1","website","contact:website"]:
                    website.append(tag.attrib["v"])
            else:
                if (tag.attrib["k"]).count(':')==0:
                    node[tag.attrib["k"]]=tag.attrib["v"]
                elif (tag.attrib["k"]).count(':')==1:
                    node[(tag.attrib["k"]).replace(':',' ')]=tag.attrib["v"]
                else:
                    pass
        if address=={}:
        	pass
        else:
        	node['address']=address

        assign(email,'email',amenity)
        assign(phone,'phone',amenity)
        assign(website,'website',amenity)
        if amenity=={}:
        	pass
        else:
        	node['amenity']=amenity

        return node
    else:
        return None


### Function to process the input file into a json file. Pretty=False ensures that output file is relatively smaller
def process_map(file_in, pretty = False):
    file_out = "{0}.json".format(file_in)
    data = []
    with codecs.open(file_out, "w") as fo:
        for _, element in ET.iterparse(file_in):
            el = shape_element(element)
            if el:
                data.append(el)
                if pretty:
                    fo.write(json.dumps(el, indent=2)+"\n")
                else:
                    fo.write(json.dumps(el) + "\n")
    fo.close()


process_map(FILE)