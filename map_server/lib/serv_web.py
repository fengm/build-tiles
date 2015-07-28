

import serv_base
import logging

class web(serv_base.service_base):
	def task(self):
		self.output_html('<html><body>Map</body></html>')

def load_zips():
	import os
	import config
	import read_zip

	_zips = {}

	_root = config.get_at('general', 'web_path')
	print 'loading zip files', _root

	for _f in os.listdir(_root):
		if _f.endswith('.zip'):
			print ' + loading zip', _f
			_zips[_f[:-4]] = read_zip.zip_file(os.path.join(_root, _f))

	print 'done'
	return _zips

_zips = None

class map(serv_base.service_base):

	def __init__(self, request, response):
		global _zips

		self.zips = _zips
		serv_base.service_base.__init__(self, request, response)

	def task(self, path):
		import os, config

		_p, _v = path.split('/', 1)

		if _p in self.zips.keys():
			_r = self.zips[_p].load(_v)
			if _r == None:
				self.output_file(config.get_at('general', 'nodata_file'))
			else:
				self.output_byte(path, _r)
		else:
			logging.info('loading web path: ' + path)
			_f = os.path.join(config.get_at('general', 'web_path'), path)
			if not os.path.exists(_f):
				_f = config.get_at('general', 'nodata_file')

			self.output_file(_f)

