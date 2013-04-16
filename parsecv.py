import referenceparser
import urllib2
import StringIO

from utils import ratelimit, jsonify

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
        http_response = urllib2.urlopen(request.form["url"])
        resource_size = int(http_response.headers["Content-Length"])
        if (resource_size > app.config["MAXIMUM_RESOURCE_SIZE"]):
            raise ValueError("Requested file size exceeds threshold: %s bytes" % resource_size)
        input_file = StringIO.StringIO()
        input_file.write(http_response.read())
        return input_file
    else:
        if not isinstance(request.files["file"], FileStorage):
            raise ValueError("Invalid file type.")
        return request.files["file"]


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

    try:
        input_file = extract_resource_from_request()
    except ValueError, e:
        return {"status": "error", "message": str(e)}
    except urllib2.HTTPError, e:
        return {"status": "error", "message": str(e)}

    try:
        pdf_file = pdf_from_resource(input_file)
    except Exception, e:
        return {"status": "error", "message": str(e)}

    try:
        text = pdf_to_text(pdf_file)
    except Exception, e:
        return {"status": "error", "message": str(e)}

    try:
        references = parse_references(text)
    except Exception, e:
        return {"status": "error", "message": str(e)}

    return references
