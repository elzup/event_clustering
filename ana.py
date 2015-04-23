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

class GeoTweets(Entity):
    using_options(tablename='gc_tweets', autoload=True)

class GeoRules(Entity):
    using_options(tablename='gc_rules', autoload=True)

metadata.bind = "%(engine)s://%(userid)s:%(passwd)s@%(host)s/%(name)s" % cfg.db
setup_all()

res = GeoTweets.query.filter(GeoTweets.timestamp >= '2015-04-21 10:00:00')\
        .filter(GeoTweets.timestamp < '2015-04-21 18:00:00').limit(10)
print(res)

data = []
for r in res:
    print(r.lotext)


_items = [
    'わたし まけ まし た わ 。',
    'わたし まけ まし た わ',
    'わたし 負け まし た わ',
    'わたし まけ まし た わ',
    'となり の きゃく は よく かき くう きゃく だ',
    'にわ には にわ なかにわ には にわ にわとり が いる',
    'バカ と テスト と 召喚獣',
    '俺 の 妹 が こんな に 可愛い わけ が ない'
]

vectorizer = TfidfVectorizer(
    use_idf=True
)
X = vectorizer.fit_transform(_items)

lsa = TruncatedSVD(10)
X = lsa.fit_transform(X)
X = Normalizer(copy=False).fit_transform(X)

km = KMeans(
    init='k-means++',
)
km.fit(X)

print(km.labels_)

