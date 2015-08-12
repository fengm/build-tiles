

import serv_base
import logging

class web(serv_base.service_base):
	def task(self):
		self.output_html('<html><body>Map</body></html>')

_zips = {}

def load_zips(load=False):
	global _zips

	if not load:
		return _zips

	import os
	import config
	import read_zip

	_root = config.get_at('general', 'web_path')
	for _f in os.listdir(_root):
		if _f.endswith('.zip'):
			_t = _f[:-4]
			if _t not in _zips:
				print ' + loading zip', _f,
				import sys
				sys.stdout.flush()

				_zips[_t] = read_zip.zip_file(os.path.join(_root, _f))
				print 'done'

	return _zips

class map(serv_base.service_base):

	def __init__(self, request, response):
		serv_base.service_base.__init__(self, request, response)

	def task(self, path):
		import os, config

		_p, _v = path.split('/', 1)

		_d_web = config.get_at('general', 'web_path')

		if os.path.exists(os.path.join(_d_web, _p)):
			logging.info('loading web path: ' + path)
			_f = os.path.join(_d_web, path)
			if not os.path.exists(_f):
				_f = config.get_at('general', 'nodata_file')

			return self.output_file(_f)

		_zips = load_zips()
		if _p not in _zips.keys():
			if os.path.exists(os.path.join(_d_web, _p + '.zip')):
				_zips = load_zips(True)

		if _p in _zips:
			_r = _zips[_p].load(_v)
			if _r == None:
				if _v.endswith('.png'):
					return self.output_file(config.get_at('general', 'nodata_file'))
				raise Exception('failed to find page %s' % path)
			else:
				return self.output_byte(path, _r)

		raise Exception('no module found %s' % _p)

