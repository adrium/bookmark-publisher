import glob
import json
from pybars import Compiler
from urllib.request import urlopen

def main(config: dict):

	templates = loadTemplates(config.get('suffix', '.tpl.html'))
	render = templates[config.get('template', 'index')]

	nilguid = '00000000-0000-0000-0000-000000000000'
	root = loadJson(config.get('bookmarks', 'Bookmarks'))
	root = root['roots']
	root = {
		'children': [ root['bookmark_bar'], root['other'], root['synced'] ],
		'guid': nilguid, 'id': 'root', 'name': 'root',
	}

	root = findGuid(root, config.get('guid', nilguid))

	structureBookmarks(root)
	processBookmarks(root, config)

	output = render(root, partials = templates)

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

	root['level'] = level

	for node in root['children']:
		processBookmarks(node, config, level + 1)

	for node in root['items']:
		node['thumbnail'] = config.get('thumbnail-placeholder', '')
		try:
			node['thumbnail'] = getThumbnail(node['url'])
		except Exception as e:
			pass

def getThumbnail(url: str):
	ytid = None
	if '/watch' in url:
		ytid = url.split('v=')[1].split('&')[0]
	if 'youtu.be/' in url:
		ytid = url.split('youtu.be/')[1].split('?')[0]
	if ytid != None:
		return 'https://i.ytimg.com/vi/ID/hqdefault.jpg'.replace('ID', ytid)

	html = ''
	with urlopen(url) as dl:
		html = dl.read().decode('utf-8')

	if '"og:image"' in html:
		return html.split('"og:image"')[1].split('content="')[1].split('"')[0]

	raise RuntimeError('No thumbnail found')

def loadTemplates(suffix: str):
	compiler = Compiler()
	result = {}
	for file in glob.glob('*' + suffix):
		name = file.replace(suffix, '')
		result[name] = compiler.compile(loadFile(file))
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
