import xml.etree.cElementTree as ET
import codecs


### Change filename accordingly 
FILE="BengaluruUrban.osm"

### Function to count the appearance of various tags in the xml
def count_main_tags(filename):
	osm_file = open(filename, "r")
	tags={}
	for event,element in ET.iterparse(osm_file):
		if element.tag in tags.keys():
			tags[element.tag]+=1
		else:
			tags[element.tag]=1
	osm_file.close()
	return tags


### Function to count the appearance of various sub-tags in the xml
def count_sub_tags(filename):
	osm_file = open(filename, "r")
	data={}
	for event, element in ET.iterparse(osm_file):
	    if element.tag == "node" or element.tag == "way":
	        for tag in element.iter("tag"):
	        	if tag.attrib['k'] in data.keys():
	        		data[tag.attrib['k']]+=1
	        	else:
	        		data[tag.attrib['k']]=1
	osm_file.close()
	return data

### Function calls to the functions defined above
###

main_tags=count_main_tags(FILE)
sub_tags=count_sub_tags(FILE)


### Writing data returned from the functions into files
with open('all_tag_types.txt',"w") as outfile:
	outfile.write('Main Tag Type'+' => '+'Number of times appeared'+'\n\n')
	for tag_type, count in main_tags.iteritems():
			outfile.write(tag_type+' => '+str(count)+'\n')

	outfile.write('\n\n\n')
	for tag_type, count in sub_tags.iteritems():
		outfile.write(tag_type+' => '+str(count)+'\n')
	outfile.close()


