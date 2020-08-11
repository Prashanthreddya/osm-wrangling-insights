from collections import defaultdict
import xml.etree.cElementTree as ET
import pprint
import re
import codecs

### Change filename accordingly 
FILE="BengaluruUrban.osm"

### open files to write the audited street names and postal codes
after_audit_street=open("after_audit_street.txt","w")
after_audit_code=open("after_audit_code.txt","w")


### RE to match a street name
street_type_re = re.compile(r'\b\S+\.?$', re.IGNORECASE)

### Mapping dictionary to map abbreviated street names to their complete name
mapping = { "Rd": "Road",
            "Rd.": "Road",
            "Ln": "Lane",
            "Ln.": "Lane",
            "Flr": "Floor",
            "Flr.": "Floor",
            "ft":"Feet",
            "ft.":"Feet",
            "Ft":"Feet",
            "Ft.":"Feet",
            "Crs":"Cross",
            "Crs.":"Cross",
            "crs":"Cross",
            "crs.":"Cross",
            "Mn":"Main",
            "Mn.":"Main",
            "Blk":"Block",
            "Blk.":"Block",
            "Opp": "Opposite",
            "Opp.": "Opposite",
            "opp": "Opposite",
            "opp.": "Opposite",
            "Ave": "Avenue",
            "Ave.": "Avenue",
            "St_try1":"Street",
            "St_try2":"Saint"
            }



### Function to update the street name using the mapping
def update_name(name, mapping):
    short_form = mapping.keys()
    name=name.split(',')
    for w in range(len(name)):
        name[w]=name[w].split()
        for i in range(len(name[w])):
            if name[w][i] in short_form:
                name[w][i]=mapping[name[w][i]]
            if name[w][-1] in ['St','ST','st','St.']:
                ### i.e, it is a STREET
                name[w][i]=mapping["St_try1"]
            else:
                for i in range(len(name[w])):
                    if name[w][i] in ['St','ST','st','St.']:
                        ### i.e, it is SAINT
                        name[w][i]=mapping["St_try2"]
    for i in range(len(name)):
        name[i]=' '.join(name[i])            
    name=', '.join(name)  
    return name


### Function to update the postal code
def update_code(code):
    for i in range(len(code)):
        if not code[i].isdigit():
            code=code.replace(code[i],' ')
    code=code.replace(' ','')

    if len(code)==6:
        return code
    else:
        return '000000'


### Audit function to audit the streetnames and postal codes
def audit(osmfile):
    
    osm_file = open(osmfile, "r")
    street_types = defaultdict(set)
    parser = ET.iterparse(osm_file, events=("start",))
    for event, elem in parser:
        if elem.tag == "node" or elem.tag == "way":
            for tag in elem.iter("tag"):
                if tag.attrib['k'] == "addr:street":
                    better_name=update_name(tag.attrib['v'],mapping)   
                    after_audit_street.write(better_name.encode('utf-8').strip() + '\n')
                elif tag.attrib['k'] == "addr:postcode":
                    better_code=update_code(tag.attrib['v'])
                    after_audit_code.write(better_code.encode('utf-8').strip() + '\n')

        elem.clear() 
    del parser
    after_audit_code.close()
    after_audit_street.close()
    osm_file.close()

audit(FILE)