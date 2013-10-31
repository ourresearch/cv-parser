import shortuuid
import os
import xml.etree.ElementTree as ET
import codecs
import re
import envoy
from unidecode import unidecode
from settings import PARSER_STRICTNESS


def parse_plaintext(body):
    """Parse plaintext and return references in a BibJSON-like dict."""
    tmpin = os.path.join("/tmp", shortuuid.uuid())
    #tmpin = shortuuid.uuid()
    body = unidecode(body)
    #print body
    print tmpin

    preprocessed_body = preprocess_body(body)
    #preprocessed_body = "References\n\n" + group_citations(preprocessed_body)
    #print preprocessed_body
    file = open(tmpin, "w")
    file.write(codecs.BOM_UTF8)
    file.write(preprocessed_body.encode("utf-8"))
    file.close()
    try:
        parsing = envoy.run("perl /Users/hpiwowar/Documents/Projects/tiv2/ParsCit/bin/citeExtract.pl -m extract_citations %s" % tmpin)
        print parsing
        text = parsing.std_out
        print text
        bibjson_citations = xml_to_bibjson(text)
    except IOError:
        return {"status": "error", "message": "Could not run parser on file"}
    try:
        # os.remove(tmpin)
        # os.remove(tmpin + ".cite")
        # os.remove(tmpin + ".body")
        pass
    except OSError:
        pass

    return bibjson_citations


def preprocess_body(body):
    body = re.sub("[ \t\r\f\v]+", " ", body)
    list_of_ways_to_say_publications = (
        "Refereed Research Publications",
        "Peer-Reviewed Publications",
        "Peer-Reviewed Journals",
        "Journal papers",
        "Published and Accepted Papers",
        "Articles",
        "Publications",
        "Publication",
    )

    list_of_things_people_write_about_after_publications = (
        "Book Chapters",
        "Workshops",
        "Workshop Papers",
        "Conference publications",
        "Conference Publications",
        "Seminars",
        "Selected Media",
        "Research Grants",
        "Research Interests",
        "Teaching:",
        "Professional Service",
        "Manuscripts",
        "Other Papers",
        "Workshop Presentations",
        "Referee Activity",
        "Talks",
        "Invited Talks",
        "Posters",
    )

    lines = body.split("\n")
    # in CVs, "References" refers to something different than in scientific
    # articles. ParsCit expects "References" to refer to published papers,
    # not people.
    for index, line in enumerate(lines):
        if "References" in line or "REFERENCES" in line:
            lines[index] = "\n"
        norm_volume = re.search("(?P<volume>\d+)\s*(?:\((?P<issue>\d+)\)|)\s*:\s*(?P<start_page>[a-zA-Z]?\d+)(-(?P<end_page>[a-zA-Z]?\d+))?", line)
        if norm_volume:
            gd = norm_volume.groupdict()
            if gd["issue"] is not None:
                if gd["end_page"] is not None:
                    replacement_string = "%s (%s), pp %s-%s" % (gd["volume"], gd["issue"], gd["start_page"], gd["end_page"])
                else:
                    replacement_string = "%s (%s), p. %s" % (gd["volume"], gd["issue"], gd["start_page"])

            else:
                if gd["end_page"] is not None:
                    replacement_string = "%s, pp %s-%s" % (gd["volume"], gd["start_page"], gd["end_page"])
                else:
                    replacement_string = "%s, p. %s" % (gd["volume"], gd["start_page"])

            lines[index] = re.sub("\d+\s*(?:\(\d+\)|)\s*:\s*[a-zA-Z]?\d+(-[a-zA-Z]?\d+)?", replacement_string, lines[index])

        marker = re.search("(?P<marker>^\d+)\.(?P<other>\D)", lines[index])
        if marker:
            gd = marker.groupdict()
            replaced = gd["marker"] + "- %s" % gd["other"]
            lines[index] = re.sub("^\d+\.[^0-9\s]", replaced, lines[index])

    found_reference_marker = 0
    found_end_marker = 0
    reference_marker = 0
    end_marker = 0

    # Preprocess the body to fit the heuristic rules used by Parscit.
    # Parscit starts parsing references when it sees a section called
    # "References" and stops when it sees "Acknowledgements". It also
    # looks for many other keywords but those were the simplest.
    for substring in list_of_ways_to_say_publications:
        for index, line in enumerate(lines):
            if not found_reference_marker:
                if substring in line or substring.upper() in line:
                    #print "Beginning Marker:", line
                    lines[index] = "References"
                    reference_marker = index
                    found_reference_marker = 1
                    break
        if found_reference_marker:
            break

    for index, line in enumerate(lines):
        if found_reference_marker and not found_end_marker:
            if index > reference_marker + 3:
                for substring in list_of_things_people_write_about_after_publications:
                    if substring in line or substring.upper() in line:
                        if index > reference_marker + 3:
                            #print "End Marker:", line
                            lines[index] = "Appendix"
                            end_marker = index
                            found_end_marker = 1
                            break
    if not found_end_marker:
        end_marker = len(lines)

    if found_reference_marker:
        body = "\n".join(lines[reference_marker:end_marker])
    else:
        body = "References\n" + "\n".join(lines)

    return body


def make_bibjson_citation(citation):
    cit = {}
    for element in citation:
        if element.tag == "authors":
            author_list = []
            for author in element:
                author_list.append({"name": author.text})
            cit["authors"] = author_list
        elif element.tag == "date":
            cit["year"] = element.text
        else:
            cit[element.tag] = element.text
    return cit


def xml_to_bibjson(xml_string):
    #print xml_string
    try:
        root = ET.fromstring(xml_string)
    except IOError:
        return {"status": "error", "message": "CV caused error in parsing process."}
    except ET.ParseError:
        return {"status": "error", "message": "Parser did not produce an output."}

    alg = root[0]
    cit_list = alg[0]
    bibjson_citations = []

    # PARSER_STRICTNESS = 0: Accept anything parsed by Parscit.
    # PARSER_STRICTNESS = 1: Accept anything determined "valid"
    #   by the automatic Parscit tester.
    # PARSER_STRICTNESS = 2: Accept only citations with a parsed
    #   "Journal" entry.
    for citation in cit_list:
        cit = make_bibjson_citation(citation)
        if PARSER_STRICTNESS == 1:
            if citation.attrib["valid"] == "true":
                if PARSER_STRICTNESS == 2:
                    if "journal" in cit:
                        bibjson_citations.append(cit)
                else:
                    bibjson_citations.append(cit)
        else:
            bibjson_citations.append(cit)

    return bibjson_citations


def group_citations(body):
    pdf_lines = body.split("\n")
    matched_citations = []
    concatenated_lines = []
    for line in pdf_lines:
        stripped_line = line.strip()
        # Check for a blank line. If line is blank and concatenated_lines
        # is non-empty, then concatenated_lines should be merged.
        if len(stripped_line) == 0:
            if len(concatenated_lines) > 0:
                matched_citations.append("\n".join(concatenated_lines))
                concatenated_lines = []
            continue

        # If concatenated_lines is empty and the line is smaller
        # than N characters, then it's probably garbage.
        if len(concatenated_lines) == 0:
            if len(stripped_line) < 30:
                continue

        concatenated_lines.append(stripped_line)

        if len(concatenated_lines) > 1:
            if 2 < len(stripped_line) < 0.70 * len(concatenated_lines[-2]):
                matched_citations.append("\n".join(concatenated_lines))
                concatenated_lines = []
                continue
            if len(stripped_line) > 4.0 * len(concatenated_lines[-2]):
                del concatenated_lines[-2]

    return "\n".join(matched_citations)
