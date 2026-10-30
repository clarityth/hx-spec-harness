import json
import threading
import unittest
from urllib.error import HTTPError
from urllib.request import urlopen
from app import Handler, ThreadingHTTPServer


class ApiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.url = f'http://127.0.0.1:{cls.server.server_port}'

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join()

    def test_sum(self):
        with urlopen(self.url + '/sum?a=2&b=3', timeout=2) as response:
            self.assertEqual(response.status, 200)
            self.assertEqual(json.load(response), {'sum': 5})

    def test_invalid(self):
        for query in ['/sum?a=2', '/sum?a=x&b=3']:
            with self.subTest(query=query):
                with self.assertRaises(HTTPError) as error:
                    urlopen(self.url + query, timeout=2)
                self.assertEqual(error.exception.code, 400)
                self.assertEqual(json.load(error.exception), {'error': 'a and b must be integers'})
