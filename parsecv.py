import referenceparser
import urllib2
import StringIO
from bs4 import BeautifulSoup

from utils import ratelimit, jsonify, get_view_rate_limit, htmlstrip

from flask import Flask, request
from werkzeug.datastructures import FileStorage

from pdfminer.pdfparser import PDFParser, PDFDocument
from pdfminer.layout import LAParams, LTTextBox, LTTextLine
from pdfminer.converter import PDFPageAggregator
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfdevice import PDFDevice


app = Flask(__name__)
app.config.from_object('settings')


def extract_resource_from_request():
    """Extracts and returns a python file type object from POST field data."""

    if not request.form and not request.files:
        raise ValueError("Received no data.")

    if request.form:
        resource_size = 0
        input_file = StringIO.StringIO()
        http_response = urllib2.urlopen(request.form["url"])

        maximum_size = app.config["MAX_CONTENT_LENGTH"]

        # open resource but keep track of the size, throw exception if size exceeded
        byte = True
        while (byte):
            byte = http_response.read(10240)
            input_file.write(byte)
            resource_size += 10240
            if resource_size > maximum_size:
                byte = False
                raise ValueError("File size threshold exceeded.")

        return input_file
    else:
        if not isinstance(request.files["file"], FileStorage):
            raise ValueError("Invalid file type.")
        return request.files["file"]


def is_pdf(resource):
    """Function to determine whether the input datatype is in PDF format."""
    resource.seek(0)
    magic_number = resource.read(4)
    resource.seek(0)
    if magic_number == "%PDF":
        return True
    else:
        return False


def pdf_from_resource(resource):
    """
    Builds PDF mining objects from input data.

    This function attempts to open a PDF file for processing.
    """
    parser = PDFParser(resource)
    document = PDFDocument()
    parser.set_document(document)

    document.set_parser(parser)
    document.initialize()

    return document


def pdf_to_text(pdf):
    """
    Takes pdfminer PDFDocument and converts to plaintext.

    Returns a string.
    """
    output = ""
    # create PDFMiner objects for data extraction
    rsrcmgr = PDFResourceManager()
    device = PDFDevice(rsrcmgr)
    interpreter = PDFPageInterpreter(rsrcmgr, device)
    laparams = LAParams()
    device = PDFPageAggregator(rsrcmgr, laparams=laparams)
    interpreter = PDFPageInterpreter(rsrcmgr, device)

    # iterate over all pages, select textbox objects and extract plaintext
    for page in pdf.get_pages():
        interpreter.process_page(page)
        layout = device.get_result()
        for element in layout:
            if isinstance(element, LTTextBox) or isinstance(element, LTTextLine):
                output += element.get_text()
    return output


def html_to_plaintext(resource):
    """Takes a file object containing HTML and returns all text elements."""

    soup = BeautifulSoup(resource)
    text = ""
    for string in soup.stripped_strings:
        text += repr(string) + '\n'

    return text


def parse_references(text):
    return referenceparser.parse_plaintext(text)


@app.route('/parsecv/', methods=['POST'])
@ratelimit(limit=app.config["REQUESTS_PER_MINUTE"], per=60)
@jsonify
def parse_request():
    """
    Process HTTP requests with associated POST data.

    Expected POST fields are:
    file -- an attached PDF file
    url -- full URL to a PDF file
    """

    text = ""

    try:
        input_file = extract_resource_from_request()

    except ValueError, e:
        return {"status": "error", "message": str(e)}
    except urllib2.HTTPError, e:
        return {"status": "error", "message": str(e)}

    if is_pdf(input_file):

        try:
            pdf_file = pdf_from_resource(input_file)
        except Exception, e:
            return {"status": "error", "message": str(e)}

        try:
            text = pdf_to_text(pdf_file)
        except Exception, e:
            return {"status": "error", "message": str(e)}

    elif request.form:
        try:
            text = html_to_plaintext(input_file)
        except Exception, e:
            return {"status": "error", "message": str(e)}

    else:

        return {"status": "error", "message": "Unsupported file format."}

    try:
        references = parse_references(text)
    except Exception, e:
        return {"status": "error", "message": str(e)}

    return references


@app.after_request
def inject_x_rate_headers(response):
    limit = get_view_rate_limit()
    if limit and limit.send_x_headers:
        h = response.headers
        h.add('X-RateLimit-Remaining', str(limit.remaining))
        h.add('X-RateLimit-Limit', str(limit.limit))
        h.add('X-RateLimit-Reset', str(limit.reset))
    return response
