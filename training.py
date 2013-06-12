import json
import re
import numpy

from sklearn.naive_bayes import GaussianNB
from sklearn.ensemble import GradientBoostingClassifier
from sklearn import cross_validation


def calculate_features(element):
    length = float(len(element))
    punctuation_rate = len(re.findall("[,.]", element)) / length
    numbers_rate = len(re.findall("\d", element)) / length
    uppercase = sum(1 for character in element if character.isupper()) / length
    words = len(re.split("\s+", element))
    return [punctuation_rate, uppercase, words, numbers_rate, length]


def calculate_set_features(items):
    """Calculate the features of every item in the set and return them, along with the labels."""
    features = []
    labels = []
    for item in items:
        for label in ("author", "title", "journal"):
            data = item.get(label)
            if not data:
                continue
            features.append(calculate_features(data))
            labels.append(label)

    return features, labels

input_dataset = json.loads(unicode(open("./publications.json").read(), "ISO-8859-1"))

features, labels = calculate_set_features(input_dataset)

# Cross-validate.
for classifier in (
        GaussianNB(),
        GradientBoostingClassifier(n_estimators=100, learning_rate=1.4, max_depth=1, random_state=0),
        ):
    scores = cross_validation.cross_val_score(classifier, features, numpy.array(labels), cv=cross_validation.KFold(len(features), n_folds=10))
    print "Final accuracy for %s: %0.3f (+/- %0.2f)" % (classifier.__class__.__name__, scores.mean(), scores.std() / 2)
