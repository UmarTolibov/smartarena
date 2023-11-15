import os

TOKEN = "6396643149:AAF3Ddb2fJCHETm5aQkwkh9SgopvT5slzy0"
WEBHOOK_PATH = f"/webhook/{TOKEN}/"
WEBHOOK_URL = "https://fastapi123-1-v3433326.deta.app" + WEBHOOK_PATH
SLI_TOKEN = "gnTHhoTY_GAgN29Beg49BRNybun9uwSqu9HFdYRF6"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))


description = """
ChimichangApp API helps you do awesome stuff. 🚀

## Items

You can **read items**.

## Users

You will be able to:

* **Create users** (_not implemented_).
* **Read users** (_not implemented_).
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
