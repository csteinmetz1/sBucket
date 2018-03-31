import json
from math import floor
import spotipy
import spotipy.util as util

keys = json.load(open('keys.json'))
username = ''
scope = 'playlist-modify-public user-top-read'

token = util.prompt_for_user_token(username, scope, client_id=keys['client_id'], 
									client_secret=keys['client_secret'], redirect_uri=keys['redirect_uri'])

if token:
	sp = spotipy.Spotify(auth=token)
	user_id = sp.me()['id']

	# create new artist/engineer/producer playlist
	playlist_id = sp.user_playlist_create(user_id, 'sBucket')['id']

	top_tracks_ids = []
	num_top_tracks = 0
	time_ranges = ['short_term', 'medium_term', 'long_term']
	for time_range in time_ranges:
		tracks = sp.current_user_top_tracks(limit=50, time_range=time_range)
		top_tracks_ids.append([track_id['id'] for track_id in tracks['items']])
		num_top_tracks += len(tracks['items'])

	print("Found {0:d} top user tracks.".format(num_top_tracks))

	rec_tracks_ids = []
	for track_list in top_tracks_ids:
		for idx in range(floor(len(track_list)/5)): # split the lists into 5 track subsets
			tracks = sp.recommendations(seed_tracks=track_list[idx*5:idx*5+5], limit=100)
			track_ids = [track_id['id'] for track_id in tracks['tracks']]
			filtered_track_ids = filter(lambda track_id : track_id not in rec_tracks_ids, track_ids)
			rec_tracks_ids += filtered_track_ids

	print("Found {0:d} unique recommended tracks.".format(len(rec_tracks_ids)))

	for idx in range(floor(len(rec_tracks_ids)/50)):
		track_ids = rec_tracks_ids[idx*50:idx*50+50]
		sp.user_playlist_add_tracks(user_id, playlist_id, track_ids)

	# currently tracks are simply ordered by the order of the top tracks
	# would be interesting to get track audio features and then order by euclidean distance