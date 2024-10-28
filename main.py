import os
import requests
from collect_links import CollectLinks

test = CollectLinks()
test.img_links(browser = 'google', topic = 'hand', limit = 0)