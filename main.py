import itertools
import numpy as np
import spotipy
import spotipy.util
from dotenv import load_dotenv, find_dotenv
import os
load_dotenv(find_dotenv())

# Create your own Spotify app to get the ID and secret.
# https://beta.developer.spotify.com/dashboard/applications
CLIENT_ID = os.environ.get('CLIENT_ID')
CLIENT_SECRET = os.environ.get('CLIENT_SECRET')

if not CLIENT_ID or not CLIENT_SECRET:
    raise Exception('No client id or secret found')

# Put your Spotify username here.
USERNAME = 'spencerc99'

REDIRECT_URI = 'http://localhost/'
SCOPE = 'user-library-read playlist-modify-public'

# Create a Spotify client that can access my saved song information.
token = spotipy.util.prompt_for_user_token(USERNAME,
                                           SCOPE,
                                           client_id=CLIENT_ID,
                                           client_secret=CLIENT_SECRET,
                                           redirect_uri=REDIRECT_URI)


sp = spotipy.Spotify(auth=token)

def get_spotify_client():
    return sp

uris = set([])

def add_uris(fetched):
    for item in fetched['items']:
        uris.add(item['track']['uri'])


results = sp.current_user_saved_tracks()
add_uris(results)
while results['next']:
    results = sp.next(results)
    add_uris(results)

# Function that returns the next n elements from the iterator. Used because
# Spotify limits how many items you can group into each of its API calls.

def grouper(n, iterable):
    it = iter(iterable)
    while True:
        chunk = tuple(itertools.islice(it, n))
        if not chunk:
            return
        yield chunk


# Get the audio features of each of the URIs fetched above.
uris_to_features = {}
for group in grouper(50, uris):
    res = sp.audio_features(tracks=group)
    for item in res:
        uris_to_features[item['uri']] = item

FEATURE_VECTOR = [
    'acousticness',
    'danceability',
    'duration_ms',
    'energy',
    'instrumentalness',
    'key',
    'liveness',
    'loudness',
    'mode',
    'speechiness',
    'tempo',
    'time_signature',
    'valence']


def features_to_vector(item):
    return np.array([item[key] for key in FEATURE_VECTOR])


vectors = [(x[0], features_to_vector(x[1])) for x in uris_to_features.items()]

# write song vector data to csv
# with open('songs.csv', 'w') as f:
#     for track, vec in vectors:
#         f.write(track + ',')
#         f.writelines(','.join([str(x) for x in vec]))
#         f.write('\n')
