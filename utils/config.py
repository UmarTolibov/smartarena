import os

TOKEN = "6396643149:AAF3Ddb2fJCHETm5aQkwkh9SgopvT5slzy0"
WEBHOOK_PATH = f"/webhook/{TOKEN}/"
WEBHOOK_URL = "https://fastapi123-1-v3433326.deta.app" + WEBHOOK_PATH
SLI_TOKEN = "gnTHhoTY_GAgN29Beg49BRNybun9uwSqu9HFdYRF6"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))


description = """
SmartArena API

## Items
Base url: `https://smartarena-bbff190dd374.herokuapp.com`

You can do **CRUD** operation with orders/stadiums.

## Users

* **Create profile**.
* **Add stadium** .
* **Order stadiums** .

## Admin/Staff

* **ALL**.

"""

html = """
<!DOCTYPE html>
<html>
    <head>
        <title>Chat</title>
    </head>
    <body>
        <h1>WebSocket Chat</h1>
        <form action="" onsubmit="sendMessage(event)">
            <input type="text" id="messageText" autocomplete="off"/>
            <button>Send</button>
        </form>
        <ul id='messages'>
        </ul>
        <script>
            var ws = new WebSocket("ws://localhost:8000/ws");
            ws.onmessage = function(event) {
                var messages = document.getElementById('messages')
                var message = document.createElement('li')
                var content = document.createTextNode(event.data)
                message.appendChild(content)
                messages.appendChild(message)
            };
            function sendMessage(event) {
                var input = document.getElementById("messageText")
                ws.send(input.value)
                input.value = ''
                event.preventDefault()
            }
        </script>
    </body>
</html>
"""