import glob
import json
from datetime import datetime, timedelta
from pybars import Compiler
from urllib.request import urlopen

def main(cfg: dict):

	defaults = {
		'bookmarks': 'Bookmarks',
		'datefmt': '%d %b %Y %H:%M',
		'guid': '00000000-0000-0000-0000-000000000000',
		'template': 'index',
		'suffix': '.tpl.html',
		'thumbnail': True,
		'thumbnail-placeholder': '',
	}

	config = defaults.copy()
	config.update(cfg)
	config['date_epoch'] = datetime(1601, 1, 1)
	config['date_scale'] = 1e6

	templates = loadTemplates(config['suffix'])
	render = templates[config['template']]

	root = loadJson(config['bookmarks'])
	root = root['roots']
	root = {
		'children': [ root['bookmark_bar'], root['other'], root['synced'] ],
		'guid': defaults['guid'], 'id': 'root', 'name': 'root',
	}

	root = findGuid(root, config['guid'])

	root['now'] = datetime.utcnow().strftime(config['datefmt'])

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
	root.update({ 'is_level%d' % i : i == level for i in range(1, 3) })
	root.update({ 'is_not_level%d' % i : i != level for i in range(1, 3) })

	for node in root['children']:
		processBookmarks(node, config, level + 1)

	for node in root['items']:
		for k in [ k for k in node.keys() if k.startswith('date_') ]:
			date = timedelta(seconds = int(node['date_added']) / config['date_scale'])
			date = date + config['date_epoch']
			node[k + '_fmt'] = date.strftime(config['datefmt'])

		node['thumbnail'] = config['thumbnail-placeholder']
		if not config['thumbnail']:
			continue
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

def loadConfig(files: list):
	result = {}
	for file in files:
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
	import sys
	main(loadConfig(sys.argv[1:]))
