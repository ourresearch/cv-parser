import urllib2
import StringIO
from settings import MAX_CONTENT_LENGTH


def get_url(url):
    resource_size = 0
    page = StringIO.StringIO()
    http_response = urllib2.urlopen(url)

    maximum_size = MAX_CONTENT_LENGTH
    # open resource but keep track of the size, throw exception if size exceeded
    byte = True
    while (byte):
        byte = http_response.read(10240)
        page.write(byte)
        resource_size += 10240
        if resource_size > maximum_size:
            byte = False
            raise ValueError("File size threshold exceeded.")
    return page
