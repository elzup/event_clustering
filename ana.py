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
from datetime import datetime
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
    timestamp = Column("timestamp", DATETIME, default=datetime.now, nullable=False)
    def __init__(self, tweet_id, latlong, rule_id, timestamp):
        self.tweet_id = tweet_id
        self.latlng = latlong
        self.rule_id = rule_id
        self.timestamp = timestamp
        self.lat = session.scalar(r.latlng.x)
        self.lng = session.scalar(r.latlng.y)

db_config = "%(engine)s://%(userid)s:%(passwd)s@%(host)s/%(name)s" % cfg.db
engine = create_engine(db_config, encoding='utf-8')

session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))

res = session.query(GeoTweets).filter(GeoTweets.timestamp >= '2015-04-21 10:00:00')\
        .filter(GeoTweets.timestamp < '2015-04-21 18:00:00').limit(1000).all()

datas = []
for r in res:
    datas.append((r.lat, r.lng))

exit()


features = np.array(datas);

# K-means クラスタリングをおこなう
# この例では 3 つのグループに分割、 10 回のランダマイズをおこなう
kmeans_model = KMeans(n_clusters=10, random_state=10).fit(features)

# 分類先となったラベルを取得する
labels = kmeans_model.labels_

texts = {}
for l in labels:
    texts[l] = []
for l, item in zip(labels, _items):
    texts[l].append(item)

for t in texts:
    print('----------' + str(t) + '---------')
    for i in texts[t]:
        print(i)

