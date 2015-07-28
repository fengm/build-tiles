# -*- coding: utf-8 -*-

'''
File: map_server.py
Author: Min Feng
Version: 0.1
Create: 2015-07-22 15:57:18
Description:
'''

def handle_error(request, response, exception):
	import json

	response.headers.add_header('Content-Type', 'application/json')
	result = {
			'status': 'error',
			'status_code': exception.code,
			'error_message': exception.explanation,
		}

	response.write(json.dumps(result))
	response.set_status(exception.code)

def main():
	_opts = _init_env()
	del _opts

	import serv_web
	serv_web._zips = serv_web.load_zips()

	_routes = [
		(r'/', 'serv_web.web'),
		(r'/map/(.+)', 'serv_web.map')
	]

	_config = {}
	_config['webapp2_extras.sessions'] = {
		'secret_key': 'something-very-secret'
	}

	import webapp2

	_app = webapp2.WSGIApplication(routes=_routes, debug=True, config=_config)
	_app.error_handlers[400] = handle_error
	_app.error_handlers[404] = handle_error

	from paste import httpserver
	import config
	httpserver.serve(_app, host=config.get_at('general', 'host'), port=config.get_at('general', 'port'))
	print 'done'

def _usage():
	import argparse

	_p = argparse.ArgumentParser()
	_p.add_argument('--logging', dest='logging')
	_p.add_argument('--config', dest='config')
	_p.add_argument('--temp', dest='temp')

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

