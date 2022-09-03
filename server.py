from sanic import Sanic
from contextvars import ContextVar
from project.models.models import Base
from project.auth.auth_bearer import extract_user_from_request
from settings import bind, async_session

app = Sanic("my_app")


_base_model_session_ctx = ContextVar("session")


async def init_db():
    async with bind.begin() as conn:
        #await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)


@app.middleware("request")
async def inject_session(request):
    request.ctx.session = async_session()
    request.ctx.session_ctx_token = _base_model_session_ctx.set(request.ctx.session)


@app.middleware("response")
async def close_session(request, response):
    if hasattr(request.ctx, "session_ctx_token"):
        _base_model_session_ctx.reset(request.ctx.session_ctx_token)
        await request.ctx.session.close()


@app.middleware("request")
async def extract_user(request):
    request.ctx.user = await extract_user_from_request(request)

