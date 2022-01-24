from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from redis import Redis 
from fastapi_utils.tasks import repeat_every
import asyncio
import strawberry
from strawberry.asgi import GraphQL
from strawberry.types import Info
from strawberry.fastapi import GraphQLRouter
import json

app = FastAPI()
r = Redis()
p = r.pubsub()
sockets = []
p.subscribe('channel')

@app.on_event("startup")
@repeat_every(seconds=0.01)
async def read():
    while msg := p.get_message():
        print('got', msg)
        for s in sockets:
            await s.send_text(msg['data'].decode())

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
    r.publish('channel', text)


@strawberry.type
class Query:
    @strawberry.field
    def hello() -> str:
        return "world"

@strawberry.type
class Subscription:
    @strawberry.subscription
    async def listen(self) -> str:
        p = r.pubsub()
        p.subscribe('channel')
        while True:
            while msg := p.get_message():
                data = msg["data"]
                if isinstance(data, int):
                    yield str(data)
                else:
                    yield msg["data"].decode()
            await asyncio.sleep(0.5)



@strawberry.type
class Query:
    @strawberry.field
    def hello(self) -> str:
        return "Hello World"



schema = strawberry.Schema(query=Query, subscription=Subscription)
graphql_app = GraphQLRouter(schema)
app.include_router(graphql_app, prefix="/graphql")