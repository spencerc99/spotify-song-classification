from main import grouper, get_spotify_client
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import numpy as np

def load_data(filename):
    """
    Loads the csv data to a list of (track_uri, vector) pairs
    """
    with open(filename, 'r') as f:
        return [(line.split(',')[0], np.array(line.split(',')[1:])) for line in f.readlines()]
data = load_data('songs.csv')
X = [x[1] for x in data]

# Normalize vector of data
scaler = StandardScaler()
X = np.array(X)
X = scaler.fit_transform(X)
scores = []
ks = range(1,25)
for k in ks:
    kmeans = KMeans(n_clusters=k).fit(X)
    scores.append(kmeans.score(X))

% matplotlib inline
import matplotlib.pyplot as plt

plt.plot(ks, scores)

scaled_data = [(data[i][0], X[i]) for i in range(len(data))]

# 10 found to be optimal k
import sklearn.cluster

RUN_ON = scaled_data

# Select the 'elbow' and classify the tracks
NUM_CLUSTERS = 10
PLAYLIST_NAME_FMT = 'Version {}: Cluster {}'
VERSION = 1

model = KMeans(n_clusters=NUM_CLUSTERS)
model.fit(X)
classified = [(x[0], model.predict(x[1])[0]) for x in RUN_ON]
sp = get_spotify_client()

# Now convert the classified songs into some playlists.
ids = []
for cluster in range(NUM_CLUSTERS):
    playlist_id = sp.user_playlist_create(USERNAME,
                                          PLAYLIST_NAME_FMT.format(VERSION, cluster))['id']
    ids.append(playlist_id)

def get_all_classified_as(classified, item_class):
    return [x[0] for x in classified if x[1] == item_class]

for cluster in range(NUM_CLUSTERS):
    tracks = get_all_classified_as(classified, cluster)
    playlist = ids[cluster]
    for group in grouper(100, tracks):
        sp.user_playlist_add_tracks(USERNAME, playlist, group)
