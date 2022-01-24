from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from redis import Redis 
from fastapi_utils.tasks import repeat_every

app = FastAPI()
r = Redis()
sockets = []

@app.on_event("startup")
@repeat_every(seconds=0.01)
async def read():
    while msg := r.lpop('channel'):
        print('got', msg)
        for s in sockets:
            await s.send_text(msg.decode())

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


@app.get("/")
async def get():
    return HTMLResponse(html)


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    sockets.append(websocket)
    send_message("Client Connected")
    try:
        while True:
            data = await websocket.receive_text()
            send_message(data)
    except WebSocketDisconnect:
        sockets.remove(websocket)
        send_message("Client Disconnected")


def send_message(text):
    print('sending', text)
    r.rpush('channel', text)
