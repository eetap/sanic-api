from sanic import Blueprint
from sanic.response import text,json
from sqlalchemy.future import select
from sanic_ext import validate
from project.models.schemas import UserIn, UserLoginBase
from project.auth.security import get_password_hash, generate_uidb64, \
    decode_uidb64, sing_jwt, verify_password, protected
from project.models.models import User
from uuid import uuid4, UUID

bp_auth = Blueprint('bp2', url_prefix='/api/auth')


@bp_auth.post("/registration")
@validate(json=UserIn)
async def sing_up(request, body: UserIn):
    session = request.ctx.session
    async with session.begin():
        data = request.json
        password_hash = get_password_hash(data['password1'])
        token = uuid4()
        user = User(username=data['username'], password_hash=password_hash, token=str(token))
        session.add(user)

    uidb64 = generate_uidb64(str(user.id))
    return json({'URL': f'http://127.0.0.1:8000/api/auth/verify/{uidb64}/{token}'})


@bp_auth.get("verify/<uidb64>/<token:uuid>")
async def verify_account(request, uidb64: str, token: UUID):
    session = request.ctx.session
    async with session.begin():
        decode_id = decode_uidb64(uidb64)
        stmt = select(User).where(User.id == int(decode_id))
        result = await session.execute(stmt)
        person = result.scalar()

        if person is not None and str(token) == person.token:
            person.is_active = True
            session.add(person)
            return json({"Message": "Вы успешно активировали аккаунт"}, status=200)
        return json({"Message": "Ссылка не действительна"}, status=404)



@bp_auth.post("/login")
@validate(json=UserLoginBase)
async def sing_in(request, body: UserLoginBase):
    session = request.ctx.session
    async with session.begin():
        data = body.dict()
        hash_pass = get_password_hash(data['password'])
        stmt = select(User).where(User.username == data['username'])
        result = await session.execute(stmt)
        person = result.scalar()

    if person is not None and verify_password(data['password'], hash_pass):
        return sing_jwt(person.username)
    return json({"Message": "Введены неправильные денные"}, status=404)



