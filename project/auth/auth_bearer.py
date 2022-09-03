import jwt
from sqlalchemy.future import select
from project.auth.security import SECRET_KEY,ALGORITHM
from project.models.models import User
from settings import async_session


async def extract_user_from_request(request):
    if request.token:
        try:
            username = jwt.decode(request.token, SECRET_KEY, algorithms=ALGORITHM)
            print(username)
        except:
            return User(username='AnonymousUser')

        async with async_session() as session:
            async with session.begin():
                stmt = select(User).where(User.username == username['userID'])
                result = await session.execute(stmt)
                person = result.scalar()

        return person
    return User(username='AnonymousUser')
