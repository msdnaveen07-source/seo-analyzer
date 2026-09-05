import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

try:
    from a2wsgi import ASGIMiddleware
    from backend.main import app
    application = ASGIMiddleware(app)
except Exception as e:
    def application(environ, start_response):
        status = '500 Internal Server Error'
        output = f'Python WSGI Initialization Error: {str(e)}'.encode('utf-8')
        response_headers = [('Content-type', 'text/plain'), ('Content-Length', str(len(output)))]
        start_response(status, response_headers)
        return [output]
