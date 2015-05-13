# -*- coding: utf-8 -*-
# machine learnign
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from sklearn.decomposition import TruncatedSVD
from sklearn.preprocessing import Normalizer
import numpy as np
# db
from sqlalchemy import *
from sqlalchemy.orm import *
from sqlalchemy.ext.declarative import declarative_base
from geoalchemy import GeometryColumn, Point
from geoalchemy.mysql import MySQLComparator
# utirity
import json
import re
from datetime import datetime
# import time
# config
import config as cfg
# ma
import MeCab

tagger = MeCab.Tagger("-Owakati")
Base = declarative_base()


class GeoTweets(Base):
    __tablename__ = "gc_tweets"
    __table_args__ = {"mysql_engine": "MyISAM"}
    id = Column("id", Integer, primary_key=True, autoincrement=True)
    tweet_id = Column("tweet_id", BigInteger)
    text = Column("text", Text)
    latlng = GeometryColumn("latlong", Point(dimension=2))
    rule_id = Column("rule_id", Integer)
    timestamp = Column("timestamp", DATETIME,
                       default=datetime.now, nullable=False)

    def __init__(self, tweet_id, latlong, rule_id, timestamp):
        self.tweet_id = tweet_id
        self.latlng = latlong
        self.rule_id = rule_id
        self.timestamp = timestamp

    def to_JSON(self):
        return {
            'id': str(self.id),
            'tweet_id': str(self.tweet_id),
            'text': str(self.text),
            'lat': str(self.lat),
            'lng': str(self.lng),
            'rule_id': str(self.rule_id),
            'timestamp': str(self.timestamp)
        }


def get_hashtag(text):
    pattern = r'#([\w一-龠ぁ-んァ-ヴーａ-ｚ]+)'
    return re.findall(pattern, text)


def save_file(filename, str):
    f = open(filename, 'w')
    f.write(str)
    f.close()

db_config = "%(engine)s://%(userid)s:%(passwd)s@%(host)s/%(name)s" % cfg.db
engine = create_engine(db_config, encoding='utf-8')
session = scoped_session(
        sessionmaker(autocommit=False, autoflush=False, bind=engine))
res = session.query(GeoTweets).filter(
        GeoTweets.timestamp >= '2015-05-10 00:00:00')\
        .filter(GeoTweets.timestamp < '2015-05-11 00:00:00').all()
print('#- record load finish')

datas = []
tag_list = {}
for r in res:
    tags = get_hashtag(r.text)
    for tag in tags:
        if not tag_list.has_key(tag):
            tag_list[tag] = []
        tag_list[tag].append(r)
print('#- tag grouping finish')

tag_list = sorted(tag_list.items(), key=lambda x: len(x[1]), reverse=True)
# 上位100件
# tag_list = tag_list[:100:]

result = []
# TODO: chose target tag
for tag, tweets in tag_list:
    for r in tweets:
        r.lat = session.scalar(r.latlng.x)
        r.lng = session.scalar(r.latlng.y)
        datas.append((r.lat, r.lng))
    features = np.array(datas)

    # K-means クラスタリングをおこなう
    # この例では 3 つのグループに分割、 10 回のランダマイズをおこなう
    kmeans_model = KMeans(n_clusters=10, random_state=1000).fit(features)

    # 分類先となったラベルを取得する
    labels = kmeans_model.labels_

    clusters = {}
    for l, data in zip(labels, tweets):
        if not clusters.has_key(str(l)):
            clusters[str(l)] = []
        clusters[str(l)].append(data.to_JSON())

    max_n = 0
    top_cluster = None
    for k, v in clusters.items():
        l = len(v)
        if max_n < l:
            max_n = l
            top_cluster = v

    result.append({
        'tag': tag,
        'top-cluster': top_cluster
    })
    if len(result) == 5:
        break

#        'clusters': clusters
str = json.dumps(result)
date_str = '2015-05-10'
save_file(date_str + '.json', str)
