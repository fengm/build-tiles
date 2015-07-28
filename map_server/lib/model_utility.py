
def proj_to_proj4(proj):
	return proj.ExportToProj4()

def proj_from_proj4(proj):
	from osgeo import osr

	_proj = osr.SpatialReference()

	import re
	_m = re.match('EPSG\s*\:\s*(\d+)', str(proj).strip())
	if _m:
		_proj.ImportFromEPSG(int(_m.group(1)))
	elif '+proj' in proj:
		_proj.ImportFromProj4(str(proj))
	else:
		_proj.ImportFromWkt(str(proj))

	return _proj

def encode_binary(txt, gz=False):
	import zlib
	import base64

	if gz:
		return base64.b64encode(zlib.compress(txt))
	return base64.b64encode(txt)

def decode_binary(txt, gz=False):
	import zlib
	import base64

	if gz:
		return zlib.decompress(base64.b64decode(txt))
	return base64.b64decode(txt)

def encode_array(dat):
	import zlib
	import base64

	return base64.b64encode(zlib.compress(dat.dumps()))

def decode_array(txt):
	import zlib
	import base64
	import numpy

	return numpy.loads(zlib.decompress(base64.b64decode(txt)))

def decode_json(txt):
	if txt == None or len(txt.strip()) == 0:
		return txt

	import json
	return json.loads(txt)

