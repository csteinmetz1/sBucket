# sBucket
Build large Spotify playlists using user top tracks and seed track recommendations.

## Setup

Install spotipy

`$ pip install spotipy`

Create the `keys.json` file and set your `client_id` and `client_secret` after creating a Spotify API app [here](https://beta.developer.spotify.com/dashboard/applications).

```
{
    "client_id" : "YOUR_CLIENT_ID",
    "client_secret" : "YOUR_CLIENT_SECRET",
    "redirect_uri" : "http://localhost:8888/callback"
}
```
## Usage

Simply run the `sbucket.py` script

`$ python sbucket.py`

This will save a new playlist to your Spotify account.

