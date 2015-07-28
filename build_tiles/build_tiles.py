'''
File: build_tiles.py
Author: Min Feng
Version: 0.1
Create: 2015-07-21 17:32:47
Description:
'''

import logging

class tiles:

	def __init__(self):
		import math
		import geo_raster_c as ge

		self.b = 6378137.0
		self.s = 256
		self.p = self.b * math.pi

		self.prj = ge.proj_from_epsg(3857)

	def list(self, level, ext=None):
		import geo_base_c as gb

		_r = (2 * self.p) / (2 ** level)

		_rows = 2 ** level
		_cols = 2 ** level

		_num = -1
		for _row in xrange(_rows):
			for _col in xrange(_cols):
				_num += 1

				_x = -self.p + (_col * _r)
				_y = -self.p + (_row * _r)

				_ext = gb.geo_extent(_x, _y, _x + _r, _y + _r, self.prj)
				if ext == None or _ext.is_intersect(ext):
					yield level, _num, _col, _row

	def extent(self, level, col, row):
		_r = (2 * self.p) / (2 ** level)
		_c = _r / self.s

		_x = -self.p + (col * _r)
		_y = -self.p + (row * _r)

		_geo = [_x, _c, 0, _y + _r, 0, -_c]

		import geo_raster_c as ge
		return ge.geo_raster_info(_geo, self.s, self.s, self.prj)

def load_shp(f):
	from osgeo import ogr
	import geo_base_c as gb

	_shp = ogr.Open(f)
	if _shp == None:
		raise Exception('Failed to load shapefile ' + f)

	_lyr = _shp.GetLayer()
	_objs = []
	_area = None

	for _f in _lyr:
		_obj = gb.geo_polygon(_f.geometry().Clone())
		_ext = _obj.extent()

		_objs.append(_obj)
		if _area == None:
			_area = _ext
		else:
			_area = _area.union(_ext)

	import geo_raster_c as ge
	_prj = ge.proj_from_epsg(3857)

	_reg = _area.to_polygon().segment_ratio(30).project_to(_prj)
	return _reg.extent()

def load_img(f, fzip):
	import geo_raster_c as ge

	_prj = ge.proj_from_epsg(3857)
	_reg = ge.open(fzip.unzip(f)).extent().to_polygon().segment_ratio(30).project_to(_prj)

	return _reg.extent()

class band:

	def __init__(self, f, fzip):
		if f.endswith('.shp'):
			import geo_raster_ex_c as gx
			self.bnd = [gx.geo_band_stack_zip.from_shapefile(f, file_unzip=fzip)]
		else:
			import geo_raster_c as ge
			_img = ge.open(fzip.unzip(f))
			self.bnd = [_img.get_band(_b + 1) for _b in xrange(_img.band_num)]

		self.color = self.bnd[0].color_table if len(self.bnd) == 1 else None

	def _color(self, c):
		_cs = {}
		if c == None:
			return _cs

		for i in xrange(256):
			_v = c.GetColorEntry(i)
			if len(_v) == 3:
				_v = list(_v) + [255]

			_cs[i] = _v

		return _cs

	def _save(self, bnd, cs, f):
		import mod_image
		_dat = mod_image.convert(bnd, cs)

		import png
		png.from_array(_dat, 'RGBA').save(f)

	def _load_color(self, f):
		import re

		_cs = {}
		with open(f) as _fi:
			for _l in _fi.read().splitlines():
				_vs = re.split('\s+', _l.strip())
				if len(_vs) < 2:
					continue

				_cc = list(map(int, re.split('\s*,\s*', _vs[1])))
				if len(_cc) == 3:
					_cc.append(255)

				_cs[int(_vs[0])] = _cc

		return _cs

	def _interp_colors(self, cs, v_non, v_val, scale=100):
		_c1 = cs[v_non]
		_c2 = cs[v_val]

		_ss = [(_c2[i] - _c1[i]) / float(scale) for i in xrange(len(_c1))]
		_cs = {}

		for i in xrange(scale + 1):
			_cs[i] = [int(_c1[_b] + (i * _ss[_b]))  for _b in xrange(len(_c1))]
			# print i, _cs[i]

		return _cs

	def _scale_band(self, bnd, div):
		import geo_raster_c as ge
		import math

		_geo = (lambda x: [x[0], x[1] / div, x[2] / div, x[3], x[4] / div, x[5] / div])(bnd.geo_transform)

		return ge.geo_band_info(_geo,
				int(math.ceil(bnd.width * float(div))),
				int(math.ceil(bnd.height * float(div))),
				bnd.proj)

	def _load_band(self, bnd):
		if len(self.bnd) == 1:
			return [self.bnd[0].read_block(bnd)]
		else:
			return [self.bnd[_b].read_block(bnd) for _b in xrange(len(self.bnd))]

	def _save_band(self, bnd, cs, f_out):
		if len(bnd) == 1:
			if bnd[0] == None:
				return
			self._save(bnd[0], cs, f_out)
		else:
			from osgeo import gdal
			_img = gdal.GetDriverByName('PNG').Create(f_out, bnd.width,\
					bnd.height, len(self.bnd), gdal.GDT_Byte)

			for _b in xrange(len(self.bnd)):
				_img.get_band(_b+1).write(self.bnd[_b].read_block(bnd).data, 0, 0)

			_img.flush()

	def make(self, bnd, f_clr, f_out):
		_cs = self._load_color(f_clr) if f_clr else self._color(self.color)
		self._save_band(self._load_band(bnd), _cs, f_out)

	def make_perc(self, bnd, val, f_clr, f_out):
		import agg_band

		_slc = 5
		_bds = self._load_band(self._scale_band(bnd, _slc))

		_bnd = []
		for _b in _bds:
			if _b == None:
				continue
			_bnd.append(agg_band.perc(_b, bnd, val[0]))

		_cs = self._interp_colors(self._load_color(f_clr) if f_clr else self._color(self.color), val[1], val[0])
		self._save_band(_bnd, _cs, f_out)

def make_tile(f, lev, num, col, row, percent, f_clr, d_out):
	import file_unzip
	import os

	with file_unzip.file_unzip() as _zip:
		_d = os.path.join(d_out, str(lev), str(col))
		try:
			os.path.exists(_d) or os.makedirs(_d)
		except Exception:
			pass

		_f = os.path.join(_d, '%s.png' % row)
		if os.path.exists(_f) and os.path.getsize(_f) > 0:
			return

		if percent != None:
			band(f, _zip).make_perc(tiles().extent(lev, col, row), percent, f_clr, _f)
		else:
			band(f, _zip).make(tiles().extent(lev, col, row), f_clr, _f)

def main():
	_opts = _init_env()

	_f_inp = _opts.input
	_d_out = _opts.output
	_f_clr = _opts.color

	import config
	import os

	os.path.exists(_d_out) or os.makedirs(_d_out)

	import file_unzip
	with file_unzip.file_unzip() as _zip:
		# detect the extent of input file
		_ext = load_shp(_f_inp) if _opts.input.endswith('.shp') else load_img(_f_inp, _zip)
		logging.info('detected extent %s' % str(_ext))
		print 'detected extent', _ext

		_ps = []
		for _lev in xrange(_opts.levels[0], _opts.levels[1]+1):
			print ' - checking level', _lev
			for _lev, _num, _col, _row in tiles().list(_lev, _ext):
				_ps.append((_f_inp, _lev, _num, _col, _row, _opts.percent, _f_clr, _d_out))

		logging.info('found %s task' % len(_ps))
		print 'found %s tasks' % len(_ps)

		print 'write map.html'
		if _opts.instance_pos == 0:
			import geo_raster_c as ge
			_ext_geo = _ext.to_polygon().segment_ratio(30).project_to(ge.proj_from_epsg()).extent()

			_f_out = os.path.join(_d_out, 'map.html')
			with open(config.cfg.get('conf', 'openlayers_temp'), 'r') as _fi, open(_f_out, 'w') as _fo:
				_fo.write(_fi.read() % {
						'title': os.path.basename(_f_inp),
						'xmin': _ext_geo.minx, 'xmax': _ext_geo.maxx,
						'ymin': _ext_geo.miny, 'ymax': _ext_geo.maxy,
						'zmin': _opts.levels[0], 'zmax': _opts.levels[1]
						})

		import multi_task
		multi_task.Pool(make_tile,
				[_ps[i] for i in xrange(_opts.instance_pos, len(_ps), _opts.instance_num)],
				_opts.task_num, True).run()

def _usage():
	import argparse

	_p = argparse.ArgumentParser()
	_p.add_argument('--logging', dest='logging')
	_p.add_argument('--config', dest='config')
	_p.add_argument('--temp', dest='temp')

	_p.add_argument('-i', '--input', dest='input', required=True)
	_p.add_argument('-o', '--output', dest='output', required=True)
	_p.add_argument('-c', '--color', dest='color')
	_p.add_argument('-p', '--percent', dest='percent', default=None, type=int, nargs=2, help='target type, background type')
	_p.add_argument('-l', '--levels', dest='levels', default=[1, 10], nargs=2, type=int)

	import multi_task
	multi_task.add_task_opts(_p)

	return _p.parse_args()

def _init_env():
	import os, sys

	_dirs = ['lib', 'libs']
	_d_ins = [os.path.join(sys.path[0], _d) for _d in _dirs if \
			os.path.exists(os.path.join(sys.path[0], _d))]
	sys.path = [sys.path[0]] + _d_ins + sys.path[1:]

	_opts = _usage()

	import logging_util
	logging_util.init(_opts.logging)

	import config
	config.load(_opts.config)

	import file_unzip as fz
	fz.clean(fz.default_dir(_opts.temp))

	return _opts

if __name__ == '__main__':
	main()

