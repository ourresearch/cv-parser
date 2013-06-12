import re
import lxml.html as ET
from utils import get_url
import urlparse


def parse_mendeley_html(base_url):
    """
    Takes a mendeley profile url.

    Returns the user's publications in bibjson format.
    """
    # We know that the parsed_url's path starts with /profiles/
    # and the scheme for mendeley urls is
    # www.mendeley.com/profiles/userid/other_things
    # so if we split the path by /, then user_id is split_path[2].
    purl = urlparse.urlparse(base_url)
    split_path = purl.path.split("/")
    user_id = split_path[2]
    sanitized_path = "/profiles/" + user_id + "/publications/journal/"
    new_url_tuple = (purl.scheme, purl.netloc, sanitized_path, "", "", "")
    url = urlparse.urlunparse(new_url_tuple)

    page = get_url(url)
    soup = ET.fromstring(page.getvalue())
    try:
        pagination = soup.get_element_by_id("user-publications").find_class("right")[0]
    except KeyError:
        return []

    num_pages = len(pagination.cssselect("div.pagemenu > ul > li"))
    if num_pages == 0:
        num_pages = 1

    citation_dict = {}
    for i in range(num_pages):
        page_url = "/".join([url, str(i)])
        page = get_url(page_url)
        soup = ET.fromstring(page.getvalue())
        citation_dict.update(parse_citation_page(soup))

    citation_list = [item for item in citation_dict.itervalues()]
    return citation_list


def parse_citation_page(soup):
    root = soup.get_element_by_id("user-publications")
    try:
        articles = root.get_element_by_id("user-publications").find_class("document-desc")
    except KeyError:
        return []

    bibjson_dict = {}
    for article in articles:
        try:
            data_text = [line.strip() for line in article.text.strip().split("\n")]
        except IndexError:
            data_text = []
        try:
            authors = [author.strip() for author in data_text[0].split(",")]
        except IndexError:
            authors = []

        try:
            title = article.cssselect("a")[0]
        except IndexError:
            title = None
        try:
            journal = article.cssselect("em")[0]
        except IndexError:
            journal = None

        try:
            vol_issue = article.cssselect("span")[0]
        except IndexError:
            vol_issue = None

        if len(authors) and title is not None:
            article_id = article.get("id")
            try:
                year = data_text[1].strip("()")
            except IndexError:
                year = None

            bibjson = {}
            bibjson["authors"] = authors
            bibjson["title"] = title.text
            if journal is not None:
                bibjson["journal"] = journal.text
            if year is not None:
                bibjson["year"] = year
            if vol_issue.text is not None:
                vol_issue_re = re.match("(?P<volume>\d+)*\s*(\((?P<issue>.*)\))*", vol_issue.text.strip())
                matched_items = vol_issue_re.groupdict()
                if matched_items["issue"] is not None:
                    bibjson["issue"] = matched_items["issue"]
                if matched_items["volume"] is not None:
                    bibjson["volume"] = matched_items["volume"]

            bibjson_dict[article_id] = bibjson
        else:
            print article.text_content()

    return bibjson_dict
