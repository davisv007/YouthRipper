import pylast

API_KEY = "a0472e3ba14a8c6b2d373f25f7214f47"  # this is a sample key
API_SECRET = "e3706cbf68860e14e3da9bf6968b66c4"

# In order to perform a write operation you need to authenticate yourself

network = pylast.LastFMNetwork(api_key=API_KEY, api_secret=API_SECRET)

# Now you can use that object everywhere
artist = network.get_artist("System of a Down")
artist.shout("<3")


track = network.get_track("Iron Maiden", "The Nomad")
track.love()
track.add_tags(("awesome", "favorite"))
