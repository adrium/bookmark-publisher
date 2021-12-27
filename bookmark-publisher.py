import glob
import json
import re
import subprocess
import time

def main(config: dict):

	root = loadJson(config['bookmarks'])
	root = root['roots']
	root = { 'guid': '-', 'children': [ root['bookmark_bar'], root['other'], root['synced'], ] }
	root = findGuid(root, config['guid'])

	structureBookmarks(root)

	output = processBookmarks(root, config)
	output = loadFile(config['template']['file']).replace('{output}', output)

	print(output)

def findGuid(root: dict, guid: str):

	if root['guid'] == guid:
		return root

	for node in root.get('children', []):
		result = findGuid(node, guid)
		if result != None:
			return result

	return None

def structureBookmarks(root: dict):

	nodes = root.pop('children', [])
	root['children'] = []
	root['items'] = []

	for node in nodes:
		if 'children' in node:
			root['children'].append(node)
			structureBookmarks(node)
		else:
			root['items'].append(node)

def processBookmarks(root: dict, config: dict, level: int = 1):

	children = items = ''

	for node in root['children']:
		children += processBookmarks(node, config, level + 1)

	for node in root['items']:
		err = 'nothumb'
		if 'thumbnail' in config:
			node['thumbnail'], err = exec(config['thumbnail'] + [ node['url'] ])
		if err != '':
			node['thumbnail'] = config['thumbnail-placeholder']
		items += config['template']['item'].format_map(node)

	root['children'] = children
	root['items'] = items
	root['level'] = level

	if root['children'] == '':
		root['children'] = config['template']['folder-empty']

	if root['items'] == '':
		root['items'] = config['template']['list-empty']
	else:
		root['items'] = config['template']['list'].format_map(root)

	result = config['template']['folder'].format_map(root)

	return result

def exec(cmd: list, input: str = ''):
	pipe = subprocess.PIPE
	p = subprocess.run(cmd, input = input.encode('utf8'), stdout = pipe, stderr = pipe)
	result = (p.stdout.decode('utf8').strip(), p.stderr.decode('utf8').strip())
	if p.returncode != 0 and result[1] == '':
		result = (result[0], 'Process returned %d' % p.returncode)
	return result

def loadConfig(files: str):
	result = {}
	for file in glob.glob(files):
		result.update(loadJson(file))
	return result

def loadJson(file: str) -> dict:
	with open(file) as f:
		return json.load(f)

def saveJson(file: str, x: dict):
	with open(file, 'w') as f:
		json.dump(x, f, indent = 2)

def loadFile(filename: str) -> str:
	with open(filename) as f:
		return f.read()

if __name__ == '__main__':
	main(loadConfig('*.json'))
