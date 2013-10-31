import parsecv
import unittest
from StringIO import StringIO
import json


class ParseCVTestCase(unittest.TestCase):

    def setUp(self):
        parsecv.app.config['TESTING'] = True
        self.app = parsecv.app.test_client()

    def tearDown(self):
        pass

    def test_get_request(self):
        result = self.app.get("parsecv/")
        self.assertEqual(result.status_code, 405)

    def test_post_wrongurl(self):
        result = self.app.post("/")
        self.assertEqual(result.status_code, 404)

    def test_post_empty(self):
        result = self.app.post("parsecv/")
        self.assertEquals(result.status_code, 422)
        data = json.loads(result.data)
        self.assertIn("Received no data", data["message"])

    # def test_bogus_file(self):
    #     result = self.app.post("parsecv/", data={"file": (StringIO("hello"), "hello.txt")})
    #     self.assertEqual(result.status_code, 422)
    #     data = json.loads(result.data)
    #     self.assertIn("Parser did not produce an output", data["message"])

    def test_ridiculously_large_file(self):
        file_length_limit = parsecv.app.config["MAX_CONTENT_LENGTH"]
        result = self.app.post("parsecv/", data={"file": (StringIO("a" * (file_length_limit + 1)), "hello.txt")})
        self.assertEqual(result.status_code, 413)

    def test_wrong_mendeley_url(self):
        result = self.app.post("parsecv/", data={"url": "http://www.mendeley.com/profiles/adfsafsf-zbyasudgasbby"})
        data = json.loads(result.data)
        self.assertIn("404", data["message"])

    def test_good_file(self):
        content = open("mikewilson.txt").read()
        result = self.app.post("parsecv/", data={"file": (StringIO(content), "hello.txt")})
        data = json.loads(result.data)
        print json.dumps(data, sort_keys=False, indent=4)
        self.assertEqual(result.status_code, 200)

        import requests
        url = "http://localhost:5001/v1/importer/bibjson?key=samplekey"
        resp = requests.post(
                url,
                data=json.dumps({
                    "input": data
                }),
                headers={'Content-type': 'application/json'}
            )
        print json.dumps(json.loads(resp.text), indent=4)
        products = json.loads(resp.text)["products"]
        tiids = products.keys()
        print tiids
        import time
        print "sleeping"
        time.sleep(3)

        url = "http://localhost:5001/v1/products/{tiids_string}?key=samplekey".format(
            tiids_string=",".join(tiids))
        resp = requests.get(
                url
            )   
        print json.dumps(json.loads(resp.text), indent=4)
        assert(1/0)       


if __name__ == '__main__':
    unittest.main()
