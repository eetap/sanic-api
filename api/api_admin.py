from sanic import Blueprint, text, json
from project.auth.security import protected
from sqlalchemy.future import select
from project.models.models import User, Account, Product
from sanic.views import HTTPMethodView
from server import app
from sanic_ext import validate
from project.models.schemas import ProductBase, ProductPatch


bp_admin = Blueprint('bp3', url_prefix='/api/admin')


@bp_admin.get("/users")
@protected
async def get_users(request):
    user = request.ctx.user
    if user.is_admin:
        session = request.ctx.session
        async with session.begin():
            query = await session.execute(select(User))
            users = query.scalars().all()
            return json([u.to_dict() for u in users])

    return text('У вас нет прав доступа')


@bp_admin.get("/bill")
@protected
async def get_check(request):
    user = request.ctx.user
    if user.is_admin:
        session = request.ctx.session
        async with session.begin():
            query = await session.execute(select(Account))
            users = query.scalars().all()
            return json([u.to_dict() for u in users])

    return text('У вас нет прав доступа')


@bp_admin.get("/users_bill/list")
@protected
async def get_bills_users(request):
    user = request.ctx.user
    if user.is_admin:
        session = request.ctx.session
        async with session.begin():
            result = await session.execute(select(User))
            users = result.scalars().all()
            list_users = [user.to_dict() for user in users]

            for user in list_users:
                stmt = select(Account).where(Account.user_id == user['id'])
                result = await session.execute(stmt)
                bills = result.scalars().all()

                if bills:
                    user['bills'] = [transaction.to_dict() for transaction in bills]
                else:
                    user['bills'] = []

            return json(list_users)
    return text('У вас нет прав доступа')


@bp_admin.get("/activate/<pk:int>")
@protected
async def get_check(request, pk: int):
    user = request.ctx.user
    if user.is_admin:
        session = request.ctx.session
        async with session.begin():
            stmt = select(User).where(User.id == pk)
            result = await session.execute(stmt)
            person = result.scalar()

            if person is not None:
                person.is_active = True
                session.add(person)
                return text(f'Вы успешно активировали аккаунт пользователя {person.username}')
            return text(f'Пользователь c id {pk} не найдет')

    return text('У вас нет прав доступа')


@bp_admin.get("/deactivate/<pk:int>")
@protected
async def get_check(request, pk: int):
    user = request.ctx.user
    if user.is_admin:
        session = request.ctx.session
        async with session.begin():
            stmt = select(User).where(User.id == pk)
            result = await session.execute(stmt)
            person = result.scalar()

            if person is not None:
                person.is_active = False
                session.add(person)
                return text(f'Вы успешно деактивировали аккаунт пользователя {person.username}')
            return text(f'Пользователь c id {pk} не найдет')

    return text('У вас нет прав доступа')


@bp_admin.post("/product")
@protected
@validate(json=ProductBase)
async def product(request, body: ProductBase):
    user = request.ctx.user
    if user.is_admin:
        session = request.ctx.session
        async with session.begin():
            data = body.dict()
            item = Product(title=data['title'],
                              description=data['description'],
                              price=data['price'])
            session.add(item)
            return text('Продукт успешно добавлен')

    return text('У вас нет прав доступа')


class AdminView(HTTPMethodView):
    decorators = [protected, ]

    async def get(self, request, pk: int):
        user = request.ctx.user
        if user.is_admin:
            session = request.ctx.session
            async with session.begin():
                stmt = select(Product).where(Product.id == pk)
                result = await session.execute(stmt)
                item = result.scalar()

            if item is not None:
                return json(item.to_dict())
            return json({'Ошибка': 'Такой товар не найден'})

        return text('У вас нет прав доступа')

    @validate(json=ProductBase)
    async def put(self, request, pk: int, body: ProductBase):
        user = request.ctx.user
        if user.is_admin:
            session = request.ctx.session
            async with session.begin():
                data = body.dict()
                stmt = select(Product).where(Product.id == pk)
                result = await session.execute(stmt)
                item = result.scalar()

                if item is not None:
                    item.title = data['title']
                    item.description = data['description']
                    item.price = data['price']
                    session.add(item)
                    return text(f'Вы успешно изменили параметры товара')
                return json({'Ошибка': 'Такой товар не найден'})

        return text('У вас нет прав доступа')

    @validate(json=ProductPatch)
    async def patch(self, request, pk: int, body: ProductPatch):
        user = request.ctx.user
        if user.is_admin:
            session = request.ctx.session
            async with session.begin():
                data = body.dict()
                stmt = select(Product).where(Product.id == pk)
                result = await session.execute(stmt)
                item = result.scalar()

                if item is not None:
                    if data['title']:
                        item.title = data['title']
                    if data['description']:
                        item.description = data['description']
                    if data['price']:
                        item.price = data['price']
                    session.add(item)
                    return text(f'Вы успешно изменили параметры товара')
                return json({'Ошибка': 'Такой товар не найден'})

        return text('У вас нет прав доступа')

    async def delete(self, request, pk: int):
        user = request.ctx.user
        if user.is_admin:
            session = request.ctx.session
            async with session.begin():
                stmt = select(Product).where(Product.id == pk)
                result = await session.execute(stmt)
                item = result.scalar()
                if item is not None:
                    await session.delete(item)
                    return text(f'Вы успешно Удалили товар')
                return text(f'Товар c id {pk} не найдет')

        return text('У вас нет прав доступа')


app.add_route(AdminView.as_view(), "/api/admin/product/<pk:int>")
