import requests
import xml.etree.ElementTree as ET
from collections import defaultdict, OrderedDict
import json
HEADERS = {
    'User-Agent': 'My SEC Parser (guddu.kumar@aitoxr.com)'
}
 
# --- Step 1: Load index.json and find relevant files
index_url = 'https://www.sec.gov/Archives/edgar/data/320193/000032019324000123/index.json'
base_url = index_url.rsplit('/', 1)[0] + '/'
index_data = requests.get(index_url, headers=HEADERS).json()
 
lab_file = pre_file = htm_file = None
for file in index_data['directory']['item']:
    name = file['name'].lower()
    if 'lab.xml' in name:
        lab_file = name
    elif 'pre.xml' in name:
        pre_file = name
    elif name.endswith('_htm.xml'):
        htm_file = name  # instance data file
 
# Fetch contents
lab_xml = requests.get(base_url + lab_file, headers=HEADERS).content
pre_xml = requests.get(base_url + pre_file, headers=HEADERS).content
htm_xml = requests.get(base_url + htm_file, headers=HEADERS).content
 
namespaces = {
    'link': 'http://www.xbrl.org/2003/linkbase',
    'xlink': 'http://www.w3.org/1999/xlink',
    'us-gaap': 'http://fasb.org/us-gaap/2023-01-31',
}
 
# --- Step 2: Label map from _lab.xml
def parse_labels(xml_data):
    tree = ET.ElementTree(ET.fromstring(xml_data))
    label_map = {}
    for label in tree.findall('.//link:label', namespaces):
        label_id = label.attrib.get('{http://www.w3.org/1999/xlink}label')
        label_text = label.text
        if label_id and label_text:
            label_map[label_id] = label_text
    return label_map
 
# --- Step 3: Hierarchy from _pre.xml
def parse_presentation(xml_data):
    tree = ET.ElementTree(ET.fromstring(xml_data))
    hierarchy = defaultdict(list)
    label_to_tag = {}
 
    for pres_link in tree.findall('link:presentationLink', namespaces):
        role = pres_link.attrib.get('{http://www.w3.org/1999/xlink}role', '')
        if 'CONSOLIDATEDSTATEMENTSOFOPERATIONS' not in role:
            continue
        for loc in pres_link.findall('link:loc', namespaces):
            label = loc.attrib['{http://www.w3.org/1999/xlink}label']
            tag = loc.attrib['{http://www.w3.org/1999/xlink}href'].split('#')[-1]
            label_to_tag[label] = tag
        for arc in pres_link.findall('link:presentationArc', namespaces):
            parent = label_to_tag.get(arc.attrib['{http://www.w3.org/1999/xlink}from'])
            child = label_to_tag.get(arc.attrib['{http://www.w3.org/1999/xlink}to'])
            if parent and child:
                hierarchy[parent].append(child)
    return hierarchy
 
# --- Step 4: First/Latest value per tag from *_htm.xml
def parse_first_values(xml_data):
    tree = ET.ElementTree(ET.fromstring(xml_data))
    values = OrderedDict()
    for elem in tree.iter():
        if elem.tag.startswith('{http://fasb.org/us-gaap/'):
            tag = elem.tag.split('}')[1]
            if tag not in values and elem.text:
                values[tag] = elem.text
    return values
 
# --- Step 5: Build JSON (clean keys, retain full tag inside object)
def build_nested_json(hierarchy, values, labels, root=None):
    def build_node(tag):
        return {
            'label': labels.get(tag, tag),
            'tag': f'us-gaap:{tag}',
            'value': values.get(tag),
            'children': {
                child: build_node(child)
                for child in hierarchy.get(tag, [])
            }
        }
 
    if not root:
        all_children = {c for v in hierarchy.values() for c in v}
        roots = [p for p in hierarchy.keys() if p not in all_children]
        root = roots[0] if roots else None
 
    if root:
        return {root: build_node(root)}
    else:
        return {}
 
# === Run Pipeline ===
labels = parse_labels(lab_xml)
hierarchy = parse_presentation(pre_xml)
values = parse_first_values(htm_xml)
json_tree = build_nested_json(hierarchy, values, labels)
 
# Save output
with open('income_statement.json', 'w') as f:
    json.dump(json_tree, f, indent=2)
 
print('✅ Clean JSON saved to income_statement.json')