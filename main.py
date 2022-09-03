from sanic.response import text
from sqlalchemy.future import select
from server import app, init_db
from sanic.signals import Event
from sanic_ext import validate
from project.models.schemas import PaymentBase
from project.auth.security import private_key, protected
from api.api_product import bp_product
from api.api_auth import bp_auth
from api.api_admin import bp_admin
from project.models.models import Account, Transaction
from Crypto.Hash import SHA1


app.blueprint(bp_product)
app.blueprint(bp_auth)
app.blueprint(bp_admin)


@app.signal(Event.SERVER_INIT_AFTER)
async def startup(app, loop):
    await init_db()


@app.post("/payment/webhook")
@protected
@validate(json=PaymentBase)
async def payment(request, body: PaymentBase):
    user = request.ctx.user
    data = body.dict()
    signature = SHA1.new()
    signature.update(
        f'{private_key}:{data["transaction_id"]}:{data["user_id"]}:{data["bill_id"]}:{data["amount"]}'.encode())
    result = signature.hexdigest()
    data["bill_id"] = str(data["bill_id"])
    if result == data['signature']:
        session = request.ctx.session
        async with session.begin():
            stmt = select(Account).where(Account.bill_id == data['bill_id'])
            result = await session.execute(stmt)
            account = result.scalar()

            if account:
                account.balance += data['amount']
                trs = Transaction(amount=data['amount'], bill_id_account=data['bill_id'])
                session.add(account)
                session.add(trs)
                return text('Ваш балан успешно пополнен')
            else:
                bill = Account(bill_id=data['bill_id'], balance=data['amount'], user_id=data['user_id'])
                trs = Transaction(amount=data['amount'], bill_id_account=data['bill_id'])
                session.add(bill)
                session.add(trs)
                return text('Создан новый счёт, ваш балан успешно пополнен')
    else:
        return text('Ошибка транзакции')


app.run(host='127.0.0.1', port='8000')

