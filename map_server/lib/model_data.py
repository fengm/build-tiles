
class geo_band:

	def __init__(self, data, geo_transform, proj, nodata, pixel_type):
		self.data = data
		self.pixel_type = pixel_type
		self.proj = proj
		self.nodata = nodata
		self.geo_transform = geo_transform

	def to_geo_band_cache(self):
		import geo_raster_c as ge
		import model_utility as mu

		return ge.geo_band_cache(mu.decode_array(self.data), self.geo_transform, mu.proj_from_proj4(self.proj), nodata=self.nodata, pixel_type=self.pixel_type)

	@staticmethod
	def from_geo_band_cache(obj):
		import model_utility as mu

		return geo_band(mu.encode_array(obj.data), obj.geo_transform, mu.proj_to_proj4(obj.proj), obj.nodata, obj.pixel_type)

	@staticmethod
	def decode(txt):
		_dat = txt['data']
		_geo = [float(_v) for _v in txt['geo_transform']]
		_proj = txt['proj']
		_pixel_type = int(txt['pixel_type'])

		_nodata = None
		if 'nodata' in txt:
			_nodata = int(txt['nodata']) if _pixel_type < 6 else float(txt['nodata'])

		return geo_band(_dat, _geo, _proj, _nodata, _pixel_type)

class data_type:

	def __init__(self):
		pass

	def encode(self, obj):
		return obj

	def decode(self, txt):
		raise NotImplementedError()

class data(data_type):

	def __init__(self, value, attrs={}):
		self.value = value

		if attrs == None:
			self.attrs = {}
		else:
			self.attrs = attrs

class data_simple(data_type):
	pass


class data_complex(data_type):
	pass


class data_numeric(data_simple):

	def __init__(self, v_min=None, v_max=None):
		data_simple.__init__(self)

		self.v_min = v_min
		self.v_max = v_max

class data_int(data_numeric):

	def decode(self, txt):
		return int(txt)

class data_float(data_numeric):

	def decode(self, txt):
		return float(txt)

class data_double(data_numeric):

	def decode(self, txt):
		return float(txt)

class data_text(data_simple):

	def decode(self, txt):
		return txt

class data_binary(data_simple):

	def decode(self, txt):
		import model_utility
		return model_utility.decode_binary(txt)

	def encode(self, obj):
		import model_utility
		return model_utility.encode_binary(obj)

class data_time(data_simple):

	def __init__(self, t_format):
		data_simple.__init__(self)
		self.t_format = t_format

	def encode(self, obj):
		return obj.strftime(self.t_format)

	def decode(self, txt):
		import datetime
		return datetime.datetime.strptime(txt, self.t_format)

class data_geometry(data_complex):

	def __init__(self, proj=None):
		data_complex.__init__(self)

		self.proj = proj

	def encode(self, obj):
		import shapely.geometry
		return shapely.geometry.mapping(obj)

	def decode(self, txt):
		import shapely.geometry
		return shapely.geometry.shape(txt)

class data_point(data_geometry):
	pass


class data_line(data_geometry):
	pass


class data_polygon(data_geometry):
	pass


class data_multi_point(data_geometry):
	pass


class data_multi_line(data_geometry):
	pass


class data_multi_polygon(data_geometry):
	pass


class data_projection(data_simple):

	def __init__(self):
		data_simple.__init__(self)

	def encode(self, obj):
		import model_utility
		return model_utility.proj_to_proj4(obj)

	def decode(self, text):
		import re
		_m = re.match('\s*EPSG\s*\:\s*(\d+)\s*', text)
		if _m:
			import geo_raster_c as ge
			return ge.proj_from_epsg(int(_m.group(1)))

		import model_utility
		return model_utility.proj_from_proj4(str(text))

class data_item:
	'''define the item for feature'''

	def __init__(self, name, dtype):
		self.name = name
		self.dtype = dtype

class data_feature(data_complex):

	def __init__(self, atts):
		data_complex.__init__(self)
		self.atts = atts

	def decode(self, txt):
		_vals = {}
		for _a in self.atts:
			_vals[_a.name] = _a.dtype.decode(txt.get(_a.name, None))

		return _vals
		# import model_data
		# return model_data.geo_feature(self.atts, _vals)

class data_band(data_complex):

	def __init__(self, v_type=None, proj=None):
		data_complex.__init__(self)

		self.v_type = v_type
		self.proj = proj

	def decode(self, txt):
		return geo_band.decode(txt).to_geo_band_cache()

	def encode(self, obj):
		_obj = obj

		import geo_raster_c as ge
		if isinstance(_obj, ge.geo_band_cache):
			_obj = geo_band.from_geo_band_cache(obj)

		return _obj

class data_extent(data_complex):

	def __init__(self, proj=None):
		data_complex.__init__(self)

		self.proj = proj

	def encode(self, obj):
		import geo_base_c as gb
		assert(isinstance(obj, gb.geo_extent))

		return data_type.encode(self, obj)

	def decode(self, txt):
		import geo_base_c as gb
		import model_utility

		_ext = gb.geo_extent(float(txt.minx), float(txt.miny), float(txt.maxx), float(txt.maxy), model_utility.proj_from_proj4(txt.proj))
		return _ext

d_numeric = data_numeric()
d_int = data_int()
d_float = data_float()
d_double = data_double()
d_text = data_text()
d_geometry = data_geometry()
d_point = data_point()
d_line = data_line()
d_polygon = data_polygon()
d_m_point = data_multi_point()
d_m_line = data_multi_line()
d_m_polygon = data_multi_polygon()
d_proj = data_projection()
d_extent = data_extent()
d_band = data_band()
d_binary = data_binary()

def convert_to_builtin_type(obj):
	import model_utility

	if type(obj).__name__ == 'SpatialReference':
		return model_utility.proj_to_proj4(obj)

	_d = {}
	for _k, _v in obj.__dict__.items():
		if _v == None:
			continue

		if isinstance(_v, list):
			if len(_v) == 0:
				continue

		# if isinstance(_v, dict):
		# 	if len(_v.keys()) == 0:
		# 		continue

		import numpy
		if isinstance(_v, numpy.ndarray):
			_d[_k] = model_utility.encode_array(_v)
			continue

		_d[_k] = _v

	if isinstance(obj, data_type):
		_d['type'] = obj.__class__.__name__.replace('data_', '')

	return _d


