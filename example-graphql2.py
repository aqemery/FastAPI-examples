import strawberry


from fastapi import FastAPI
from strawberry.types import Info
from strawberry.fastapi import GraphQLRouter


async def notify_new_flavour(name: str):
    print(name)


@strawberry.type
class Query:
    @strawberry.field
    def hello(self) -> str:
        return "Hello World"


@strawberry.type
class Mutation:
    @strawberry.mutation
    def create_flavour(self, name: str, info: Info) -> bool:
        info.context["background_tasks"].add_task(notify_new_flavour, name)
        return True


schema = strawberry.Schema(Query, Mutation)
graphql_app = GraphQLRouter(schema)

app = FastAPI()
app.include_router(graphql_app, prefix="/graphql")
