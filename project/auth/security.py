from passlib.context import CryptContext
import jwt
import base64
from functools import wraps
from sanic import text, json
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

SECRET_KEY = os.getenv('SECRET_KEY')
ALGORITHM = os.getenv('ALGORITHM')
private_key = os.getenv('PRIVATE_KEY')
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

#dad
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def token_response(token: str):
    return json({'access token': token})


def sing_jwt(userID):
    payload = {
        'userID': str(userID),
        'iat': datetime.now(),
        "exp": datetime.now() + timedelta(days=0, minutes=20)
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return token_response(token)


def check_token(request):
    if not request.token:
        return False
    try:
        jwt.decode(
            request.token, SECRET_KEY, algorithms=ALGORITHM
        )
    except jwt.exceptions.InvalidTokenError:
        return False
    else:
        return True


def protected(wrapped):
    def decorator(f):
        @wraps(f)
        async def decorated_function(request, *args, **kwargs):
            is_authenticated = check_token(request)

            if is_authenticated:
                response = await f(request, *args, **kwargs)
                return response
            else:
                return text("Вы не авторизованы.", 401)

        return decorated_function

    return decorator(wrapped)


def generate_uidb64(uidb64):
    encoded = base64.urlsafe_b64encode(uidb64.encode('UTF-8'))
    result = encoded.decode('UTF-8')
    return result


def decode_uidb64(encoded):
    rslt = encoded.encode('UTF-8')
    data = base64.urlsafe_b64decode(rslt)
    result = data.decode('UTF-8')
    return result
