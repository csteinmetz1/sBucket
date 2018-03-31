import sys
import json
from math import floor
import spotipy
import spotipy.util as util

keys = json.load(open('keys.json'))
username = ''
scope = 'playlist-modify-public user-top-read'

token = util.prompt_for_user_token(username, scope, client_id=keys['client_id'], 
									client_secret=keys['client_secret'], redirect_uri=keys['redirect_uri'])

class sbucket():
	def __init__(self, limit, token):
		if token:
			self.sp = spotipy.Spotify(auth=token)
			self.user_id = self.sp.me()['id']
			self.limit = limit
			self.done = False

	def get_top_tracks(self):
		top_tracks_ids = []
		num_top_tracks = 0
		time_ranges = ['short_term', 'medium_term', 'long_term']
		for time_range in time_ranges:
			tracks = self.sp.current_user_top_tracks(limit=50, time_range=time_range)
			top_tracks_ids += ([track_id['id'] for track_id in tracks['items']])

		print("Found {0:d} top user tracks for initial seeds.".format(len(top_tracks_ids)))
		return top_tracks_ids

	def get_recommendations(self, seed_track_ids):
		rec_tracks_ids = []
		for idx in range(floor(len(seed_track_ids)/5)): # split the lists into 5 track subsets
			tracks = self.sp.recommendations(seed_tracks=seed_track_ids[idx*5:idx*5+5], limit=25)
			track_ids = [track_id['id'] for track_id in tracks['tracks']]
			filtered_track_ids = filter(lambda track_id : track_id not in rec_tracks_ids or track_id not in seed_track_ids, track_ids)
			rec_tracks_ids += filtered_track_ids
			sys.stdout.write("Added {0:d} new and unique recommended tracks...\r".format(len(rec_tracks_ids)))
			sys.stdout.flush()
			if len(rec_tracks_ids) + len(seed_track_ids) > self.limit:
				self.done = True
				print("\nTrack limit reached! [{0:d}]".format(self.limit))
				break

		print("Found total of {0:d} new and unique recommended tracks.".format(len(rec_tracks_ids) + len(seed_track_ids)))
		return rec_tracks_ids

	def add_tracks_to_playlist(self, playlist_name, track_ids):
		# create new artist/engineer/producer playlist
		playlist_id = self.sp.user_playlist_create(self.user_id, playlist_name)['id']
		for idx in range(floor(len(track_ids)/50)):
			track_ids_set = track_ids[idx*50:idx*50+50]
			self.sp.user_playlist_add_tracks(self.user_id, playlist_id, track_ids_set)
		print("Saved {0:d} new tracks to an sBucket playlist.".format(len(track_ids)))
		# currently tracks are simply ordered by the order of the top tracks
		# would be interesting to get track audio features and then order by euclidean distance

keys = json.load(open('keys.json'))
username = ''
scope = 'playlist-modify-public user-top-read'
token = util.prompt_for_user_token(username, scope, client_id=keys['client_id'], 
									client_secret=keys['client_secret'], redirect_uri=keys['redirect_uri'])

sBucket = sbucket(5000, token)
top_tracks = sBucket.get_top_tracks()
rec_tracks = sBucket.get_recommendations(top_tracks)

i = 0
while(not sBucket.done):
	print("Starting recursion {0:d}...".format(i+1))
	rec_tracks += sBucket.get_recommendations(rec_tracks)
	i += 1

sBucket.add_tracks_to_playlist('sBucket', rec_tracks)