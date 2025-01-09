> [!IMPORTANT]
> Due to massive cuts in Spotify API functionalities I am sad to inform that project PlaylistDJ is no longer usable :(



# About Project

## Vision

**PlaylistsDJ** was created to let Spotify users to have more control over music they want to listen. Often people have huge playlists with songs differing greatly in mood which is most times inconvinient - that is where **PlaylistsDJ** can help you in managing this chaos! Application can be used in many ways, for example:
* **Gaming 🎮** - Do you need the fastest, most energetic songs on your playlist because you are fighting for a higher division in your favorite game? Or maybe you want to make songs queue that will start at most chill songs and will slowly become more and more energetic to enchance your gaming experience? You will surely love this app!
  
* **TTRPGs 🎲** - Instead of juggling multiple playlists you can simply put them in one playlist and use few sliders to easily transition from high-energy battle music to serene tunes for a relaxing tavern visit after a successful fight. You can also use route searching feature to smoothly go from one mood to another! (Fun fact: this app was inspired by the creator’s need for a tool like this for their D&D campaigns!)

* **Playing music on parties 🎧** - Have your Spotify ever surprised you on a party by switching from Pitbull to Lana Del Rey (whole mood ruined! ofc you put Lana in this playlist... but it was for 3am life talks not for Spotify to ruin everyone's dancing mood!). Now you can keep your playlist focused on a consistent mood and avoid situations like this.

## Features 
> [!NOTE]
> **PlaylistsDJ** uses audio features provided by Spotify. Note that not all songs might be correctly clasified by some Spotify algorithms.


### 1. **Player**

  **Player** is a main screen of this app. Includes some features from SpotifyPlayer like pausing song, skipping to next song or browsing current queue (current version doesn't allow for removing songs from queue, for this purpouse you have to use your original SpotifyPlayer). On Player screen you also should load playlist that the application will use. From this screen you can access two queue-controlling features - **Mood Searcher**
  and **Route Searcher**.

  ![image](https://github.com/thesun901/PlaylistsDJ/assets/70859223/bacd9b6f-ef12-46c5-8ea9-bac754f2ce93)


### 2. **Mood Searcher**

**Mood searcher** is a feature that allows you to find songs closest to chosen mood expressed by chosen parameters.
  ![image](https://github.com/thesun901/PlaylistsDJ/assets/70859223/28d527ca-ea1a-4d36-84b3-2b93636fdcfe)


### 3. **Route Searcher**
**Route Searcher** is a feature that finds smooth, shortest path beetween two chosen set of parameters.
![image](https://github.com/thesun901/PlaylistsDJ/assets/70859223/8d56cb8b-dc99-4649-81c2-8f39c011e6ed)

## Downloading

App doesn't have a full downloadable release yet. For most cases to use it you should download code and connect it to your own *Spotify for Developers* account.

However if you are really interested in just using this app you can email me at: oliwier.dygdalowicz@gmail.com


# Code

## How to run this code?

To run this app you have to connect this app with your own *Spotify for Developers* account, get your *client id* and *client secret*, add .env file and put your *client id* and *client secret* there. Step by step instruction below:

1. Create new  *Spotify for Developers* account on [this site](https://developer.spotify.com)
2. Go to [Dashboard](https://developer.spotify.com/dashboard) > Create new app
3. Fill the informations and save your app
> [!NOTE]
> Name of your app and description are up to your choice.
> 
> Redirect URI isn't really important in here, but if you want to be sure nothing will go wrong you can put simply: 'http://localhost:3000'
> 
> To run own copy of this app you **HAVE TO** check at least ***Web API*** and Web ***Playback SDK*** in *Which API/SDKs are you planning to use?* section

4. After your app is created go to your app page and then to settings. You should have your Client ID and Client Secret in there
> [!WARNING]
> Do not share your Client ID and Client Secret with anyone!

5. Download PlaylistsDJ from here
6. Add '.env' file in main project folder
7. inside '.env' file put those two lines:
```
client_id = <YOUR CLIENT ID HERE>
client_secret = <YOUR CLIENT SECRET HERE>
```
8. Now your copy of **PlaylistsDJ** should be ready to run!


## Structure

Here's quick summary about content of files:
- ***spotify_setup.py*** - authorizes usage of Spotify API using [spotipy module](https://spotipy.readthedocs.io/en/2.24.0/) from this file you should import *sp* variable to make Spotify API calls
- ***main_GUI.py*** - contains functionalities of kivy widgets - from here some API calls are being made directly
- ***main.kv, one_point_search.kv, route_search.kv*** - structural files in [kvlang](https://kivy.org/doc/stable/guide/lang.html) that describe placement of widgets on **Player, Mood Searcher** and **Route Searcher** screens
- ***spotify_objects.py*** - defines Playlist, Track, TrackNode and TracksGraph classes. TracksGraph converts Playlist object to a n-dimentional graph containing Tracks represented as TrackNodes; implements **Mood Searcher** (just by finding closests songs to chosen mood, which doesnt require using graph) and **Route Searcher** (using Dijkstra Algorithm) functionalities
- ***playback_state_functions.py, processing_functions.py*** - contain some helping functions for example: getting playlistID from given URL, getting all tracks from given playlistID etc.
