import parsecv
import unittest
import StringIO
import json
import requests
import time

def parse_free_text(content):
    result = app.post("parsecv/", 
                data={"file": (StringIO.StringIO(content), 
                    "hello.txt")})
    bibjson_data = json.loads(result.data)

    #print json.dumps(bibjson_data, sort_keys=False, indent=4)
    return bibjson_data

def get_tiids_from_bibjson(api_root, bibjson_data):
    url = api_root + "/v1/importer/bibjson?key=samplekey"
    resp = requests.post(
            url,
            data=json.dumps({
                "input": bibjson_data
            }),
            headers={'Content-type': 'application/json'}
        )
    #print json.dumps(json.loads(resp.text), indent=4)
    products = json.loads(resp.text)["products"]
    tiids = products.keys()
    print tiids
    return tiids


def get_products(api_root, tiids):
    url = api_root + "/v1/products/{tiids_string}?key=samplekey".format(
        tiids_string=",".join(tiids))
    resp = requests.get(
            url
        )   
    print json.dumps(json.loads(resp.text), indent=4)
    return {"url": url, "products":resp.text}

def add_tiids_to_profile(webapp_root, user_id, tiids):
    url = webapp_root + "/user/{user_id}/products?key=samplekey".format(
        user_id=user_id)

    resp = requests.put(
            url,
            data=json.dumps({
                "tiids": tiids
            }),
            headers={'Content-type': 'application/json'}            
        )
    #print resp.text
    return resp.text





#parsecv.app.config['TESTING'] = True
app = parsecv.app.test_client()

# api_root = "http://localhost:5001"
# webapp_root = "http://localhost:5000"
api_root = "http://api.impactstory.org"
webapp_root = "http://impactstory.org"

# filename = "mike.txt"
# user_id = 5032

# take stuff from freetext file and write the parsed bibjson into a file
if False:
    lines = open(filename).readlines()
    bibjson_data_list = []
    for line in lines:
        bibjson_data_list += parse_free_text(line)

    print json.dumps(bibjson_data_list, indent=4)
    bibjson_file = open("bibjson.txt", "w")
    bibjson_file.write(json.dumps(bibjson_data_list, indent=4))
    bibjson_file.close()

# take stuff from parsed bibjson and create tiids
if True:
    bibjson_reread_lines = json.loads(open("bibjson.txt", "r").read())

    tiids = []
    lines_with_no_tiid = []
    for bibjson_data in bibjson_reread_lines:
        tiid_in_a_list = get_tiids_from_bibjson(api_root, [bibjson_data])
        if not tiid_in_a_list:
            print "no tiid created for", line
            lines_with_no_tiid += [line]
        tiids += tiid_in_a_list

    print tiids
    print "number of tiids:", len(tiids)
    print "number of lines with no tiids:", len(lines_with_no_tiid)
    print "lines with no tiids:\n", "\n".join(lines_with_no_tiid)

# add tiids to someone's profile
if True:
    print "adding tiids to profile"
    resp = add_tiids_to_profile(webapp_root, user_id, tiids)
    print "added tiids to profile"

# look at products
if False:
    print "sleeping while data is gathered"
    time.sleep(5)
    resp = get_products(api_root, tiids)
    print resp["products"]
    print resp["url"]


# make a profile in webapp, but not working properly yet

# user_dict = {
#     "password": "pass",
#     "alias_tiids": {},
#     "external_profile_ids": {"orcid":None, "github":None, "slideshare":None},
#     "url_slug": "MikeWilson", 
#     "email": str(time.time()) + "@example.com",
#     "given_name": "Mark", 
#     "surname": "Wilson"
#     }

# def make_profile(webapp_root, user_dict, tiids):
#     url = webapp_root + "/creating".format(
#         tiids_string=",".join(tiids))
#     resp = requests.post(
#             url,
#             data={"user-dict-json": json.dumps(user_dict)}
#         )
#     print resp.text
#     return user_dict["url_slug"]

