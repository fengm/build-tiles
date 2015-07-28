
import logging

class zip_file:

	def __init__(self, f):
		import zipfile
		self.obj = zipfile.ZipFile(f)

		# print 'searching in the zip file'
		logging.info('searching in the zip file')
		self.names = self.obj.namelist()
		logging.info('found %s files' % len(self.names))

		# print 'searching root'
		# search for the root
		self.root = self._search_root(self.names)
		logging.info('root %s' % self.root)

	def load(self, f):
		_f = '%s/%s' % (self.root, f) if self.root else f
		if _f not in self.names:
			return None

		# self.obj.extract(self.obj.getinfo(_f), 'test')
		return self.obj.read(_f)

	def _search_root(self, ns):
		import os

		for _n in ns:
			if _n.endswith('.html'):
				return os.path.dirname(_n)

		raise Exception('failed to locate the root')

def main():
	_z = zip_file(r'h:\mfeng\test\glcf\fcc_1975\test\map\test1\water_2000.zip')

	_f = '10/917/500.png'
	print 'read', _f
	with open('500.png', 'wb') as _fo:
		_fo.write(_z.load(_f))

def _init_env():
	import os, sys

	_dirs = ['lib', 'libs']
	_d_ins = [os.path.join(sys.path[0], _d) for _d in _dirs if \
			os.path.exists(os.path.join(sys.path[0], _d))]
	sys.path = [sys.path[0]] + _d_ins + sys.path[1:]

if __name__ == '__main__':
	_init_env()
	main()

