from app.services import AbstractAuthService
from app.models import User, JwtTokenSchema, TokenPair
from app.repositories import get_auth_repo, get_user_repo

from datetime import timedelta, datetime, timezone

from jose import jwt, JWTError

from app.core.exceptions import AuthFailedException
from app.core.config import auth_settings

from uuid import uuid4

SUB = "sub"
EXP = "exp"
IAT = "iat"
JTI = "jti"


class AuthService(AbstractAuthService):
    # Singleton
    def __new__(cls):
        if not hasattr(cls, "instance"):
            cls.instance = super(AuthService, cls).__new__(cls)
        return cls.instance

    def __init__(self) -> None:
        self.auth_repo = get_auth_repo()
        self.user_repo = get_user_repo()

    async def authorize(self, email: str, password: str) -> User | None:
        db_user = await self.auth_repo.authorize(email, password)
        if db_user is None:
            return None
        return User.model_validate(db_user, from_attributes=True)

    @staticmethod
    def create_token(user: User) -> TokenPair:
        token_pair = AuthService._create_token_pair(user=user)
        return token_pair

    @staticmethod
    def get_expire_time() -> int:
        exp = datetime.now(timezone.utc) + timedelta(
            minutes=auth_settings.REFRESH_TOKEN_EXPIRES_MINUTES
        )
        exp.replace(tzinfo=timezone.utc)
        return int(exp.timestamp())

    async def decode_access_token(self, token: str):
        try:
            data = jwt.decode(
                token,
                auth_settings.SECRET_KEY,
                algorithms=[auth_settings.ALGORITHM],
            )
            banned_token = await self.auth_repo.get_banned_token_by_id(data[JTI])
            if banned_token:
                raise JWTError("This token is banned")
        except JWTError:
            raise AuthFailedException()

        return data

    async def add_banned_token(self, id, expired):
        return self.auth_repo.add_banned_token(id, expired)

    async def get_current_active_user(self, token: str) -> User:
        try:
            data = await self.decode_access_token(token=token)

            user_id = data.get(SUB, None)

            if user_id is None:
                raise AuthFailedException("Invalid token format")

            user = self.user_repo.get_user_by_id(id=user_id)
            if user is None:
                raise AuthFailedException("User not found")

            return User.model_validate(user, from_attributes=True)
        except JWTError:
            AuthFailedException("Invalid token")

    @staticmethod
    def refresh_token_state(token: str):
        try:
            data = jwt.decode(
                token,
                auth_settings.SECRET_KEY,
                algorithms=[auth_settings.ALGORITHM],
            )
        except JWTError:
            raise AuthFailedException()

        return {"token": AuthService._create_access_token(data=data).token}

    @staticmethod
    @staticmethod
    def _get_utc_current():
        return datetime.now(timezone.utc)

    @staticmethod
    def _create_access_token(data: dict, minutes: int | None = None) -> JwtTokenSchema:
        expiration_date = AuthService._get_utc_current() + timedelta(
            minutes=minutes or auth_settings.ACCESS_TOKEN_EXPIRES_MINUTES
        )

        data[EXP] = expiration_date

        token = JwtTokenSchema(
            token=jwt.encode(
                data,
                auth_settings.SECRET_KEY,
                algorithm=auth_settings.ALGORITHM,
            ),
            payload=data,
            expire=expiration_date,
        )

        return token

    @staticmethod
    def _create_refresh_token(data: dict) -> JwtTokenSchema:
        expiration_date = AuthService._get_utc_current() + timedelta(
            auth_settings.REFRESH_TOKEN_EXPIRES_MINUTES
        )

        data[EXP] = expiration_date

        token = JwtTokenSchema(
            token=jwt.encode(
                data,
                auth_settings.SECRET_KEY,
                algorithm=auth_settings.ALGORITHM,
            ),
            payload=data,
            expire=expiration_date,
        )

        return token

    @staticmethod
    def _create_token_pair(user: User) -> TokenPair:
        data = {
            SUB: str(user.id),
            JTI: str(uuid4()),
            IAT: AuthService._get_utc_current(),
        }

        return TokenPair(
            access=AuthService._create_access_token(data={**data}),
            refresh=AuthService._create_refresh_token(data={**data}),
        )
