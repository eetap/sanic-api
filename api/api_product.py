from sanic import json, text
from sanic import Blueprint
from project.models.models import Product, Account, Transaction
from sqlalchemy.future import select
from project.auth.security import protected

bp_product = Blueprint('bp1', url_prefix='/api')


@bp_product.get("/product/list")
@protected
async def get_products(request):
    session = request.ctx.session
    async with session.begin():
        product = await session.execute(select(Product))
        products = product.scalars().all()

    return json([product.to_dict() for product in products])


@bp_product.get("/buy/product/<pk:int>")
@protected
async def buy_product(request, pk: int):
    user = request.ctx.user
    if user.is_active:
        session = request.ctx.session
        async with session.begin():
            stmt = select(Product).where(Product.id == pk)
            result = await session.execute(stmt)
            item = result.scalar()

            if item is None:
                return json({"Message": "Нет такого продукта"}, status=404)

            stmt = select(Account).where((Account.user_id == user.id) & (Account.balance >= item.price))
            result = await session.execute(stmt)
            account = result.scalar()

            if account is not None:
                account.balance -= item.price
                session.add(account)
                return json({"Message": "Операция совершена"}, status=200)
            return json({"Message": "На вашем аккаунте недостаточно средств"}, status=404)
    else:
        return json({"Message": "Ваш аккаунт не активирован"}, status=404)



@bp_product.get("/bill/list")
@protected
async def get_bills(request):
    user = request.ctx.user
    if user.is_active:
        session = request.ctx.session
        async with session.begin():
            result = await session.execute(select(Account).where(Account.user_id == user.id))
            bills = result.scalars().all()

            if bills:
                list_bills = [bill.to_dict() for bill in bills]

                for bill in list_bills:
                    stmt = select(Transaction).where(Transaction.bill_id_account == bill['bill_id'])
                    result = await session.execute(stmt)
                    transactions = result.scalars().all()

                    if transactions:
                        bill['transaction'] = [transaction.to_dict() for transaction in transactions]
                return json(list_bills)
            return json({"Message": "У вас еще нет ни одно счёта"}, status=404)
    return json({"Message": "Ваш аккаунт не активирован"}, status=404)

