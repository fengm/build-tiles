import numpy as np
cimport numpy as np
cimport cython

@cython.boundscheck(False)
@cython.wraparound(False)

def convert(bnd, cs):
	cdef np.ndarray[np.uint8_t, ndim=2] _dat = bnd.data
	cdef int _rows = bnd.height, _cols = bnd.width
	cdef int _row, _col, _val

	# cdef np.ndarray[np.uint8_t, ndim=3] _out = np.zeros((4, _rows, _cols), dtype=np.uint8)

	_out = []
	_blk = [0, 0, 0, 0]
	for _row in xrange(_rows):
		_rrr = []
		for _col in xrange(_cols):
			_val = _dat[_row, _col]

			if _val not in cs:
				_rrr.extend(_blk)
				continue

			if bnd.nodata != None and bnd.nodata == _val:
				_rrr.extend(_blk)
				continue

			_c = cs[_val]

			# _out[:, _row, _col] = _c
			_rrr.extend(_c)
		_out.append(_rrr)

	return _out

def update(dat, idx, ref):
	if dat.dtype == np.uint8:
		return update_uint8(dat, idx, ref)

	if dat.dtype == np.float32:
		return update_float(dat, idx, ref)

	if dat.dtype == np.int16:
		return update_int16(dat, idx, ref)

	raise Exception('unsupported data type')

def update_uint8(np.ndarray[np.uint8_t, ndim=2] dat, np.ndarray[np.uint8_t, ndim=2, cast=True] idx, \
		np.ndarray[np.uint8_t, ndim=2] ref):
	cdef int _rows = dat.shape[0]
	cdef int _cols = dat.shape[1]
	cdef int _row, _col, _i
	cdef int _v, _r

	for _row in xrange(_rows):
		for _col in xrange(_cols):
			_i = idx[_row, _col]

			if _i > 0:
				dat[_row, _col] = ref[_row, _col]

def update_float(np.ndarray[np.float32_t, ndim=2] dat, np.ndarray[np.uint8_t, ndim=2, cast=True] idx, \
		np.ndarray[np.float32_t, ndim=2] ref):
	cdef int _rows = dat.shape[0]
	cdef int _cols = dat.shape[1]
	cdef int _row, _col, _i
	cdef float _v, _r

	for _row in xrange(_rows):
		for _col in xrange(_cols):
			_i = idx[_row, _col]

			if _i > 0:
				dat[_row, _col] = ref[_row, _col]

def update_int16(np.ndarray[np.int16_t, ndim=2] dat, np.ndarray[np.uint8_t, ndim=2, cast=True] idx, \
		np.ndarray[np.int16_t, ndim=2] ref):
	cdef int _rows = dat.shape[0]
	cdef int _cols = dat.shape[1]
	cdef int _row, _col, _i
	cdef int _v, _r

	for _row in xrange(_rows):
		for _col in xrange(_cols):
			_i = idx[_row, _col]

			if _i > 0:
				dat[_row, _col] = ref[_row, _col]
