# -*- coding: utf-8 -*-
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from sklearn.decomposition import TruncatedSVD
from sklearn.preprocessing import Normalizer

import unittest
from datetime import datetime
from elixir import *

import numpy as np
import config as cfg

import MeCab
tagger = MeCab.Tagger("-Owakati")


class GeoTweets(Entity):
    using_options(tablename='gc_tweets', autoload=True)

class GeoRules(Entity):
    using_options(tablename='gc_rules', autoload=True)

metadata.bind = "%(engine)s://%(userid)s:%(passwd)s@%(host)s/%(name)s" % cfg.db
setup_all()

res = GeoTweets.query.filter(GeoTweets.timestamp >= '2015-04-21 10:00:00')\
        .filter(GeoTweets.timestamp < '2015-04-21 18:00:00').limit(1000)

_items = []
for r in res:
    _items.append(tagger.parse(r.text))

vectorizer = TfidfVectorizer(
    use_idf=True
)
X = vectorizer.fit_transform(_items)

lsa = TruncatedSVD(20)
X = lsa.fit_transform(X)
X = Normalizer(copy=False).fit_transform(X)

km = KMeans(
    init='k-means++',
)
km.fit(X)
labels = km.labels_

texts = {}
for l in labels:
    texts[l] = []
for l, item in zip(labels, _items):
    texts[l].append(item)

for t in texts:
    print('----------' + str(t) + '---------')
    for i in texts[t]:
        print(i)
