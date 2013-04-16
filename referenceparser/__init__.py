STUB = [
        {
            "bibnumber": "3.1",
            "school": "Dept. Prob. and Stat., University of Sheffield",
            "title": "Stopping time identities and limit theorems for Markov chains",
            "author": [
                "Pitman, J W"
                ],
            "collection": "pitnoid",
            "id": "p74t",
            "year": "1974",
            "keywords": [
                "Stopping time",
                "Identities",
                "Markov chain",
                "Occupation time",
                "Rate of convergence",
                "Transition probabilities",
                "Coupling"
                ],
            "type": "phdthesis"
            },
        {
            "bibnumber": "9",
            "title": "Birth, death and conditioning of Markov chains",
            "journal": "Annals of Probability",
            "author": [
                "Jacobsen, M",
                "Pitman, J W"
                ],
            "mrclass": "60J10",
            "collection": "pitnoid",
            "volume": "5",
            "id": "jp77",
            "mrnumber": "MR0445613",
            "year": "1977",
            "keywords": [
                "Path decomposition",
                "Conditioned process",
                "Conditional independence",
                "Markov chain",
                "Birth time",
                "Death time"
                ],
            "type": "article",
            "pages": "430 to 450",
            "znumber": "0363.60052"
            },
        ]


def parse_plaintext(body):
    """Parse plaintext and return references in a BibJSON-like dict."""
    return STUB


def parse_html(body):
    """Parse html and return references in a BibJSON-like dict."""
    return STUB
