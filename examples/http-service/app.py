from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import os
from urllib.parse import urlparse, parse_qs


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        url = urlparse(self.path)
        if url.path == '/':
            content = '<meta charset="utf-8"><h1>합계 API 연습</h1><p>/sum?a=2&b=3을 열면 합계 5를 반환합니다.</p>'.encode()
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
        else:
            query = parse_qs(url.query)
            try:
                if url.path != '/sum':
                    raise ValueError('unknown path')
                value = {'sum': int(query['a'][0]) + int(query['b'][0])}
                status = 200
            except (KeyError, ValueError):
                value, status = {'error': 'a and b must be integers'}, 400
            content = json.dumps(value).encode()
            self.send_response(status)
            self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(content)))
        self.end_headers()
        self.wfile.write(content)

    def log_message(self, *args):
        pass


if __name__ == '__main__':
    server = ThreadingHTTPServer(('0.0.0.0', int(os.environ.get('PORT', '3000'))), Handler)
    print(f'Port {server.server_port}', flush=True)
    server.serve_forever()
