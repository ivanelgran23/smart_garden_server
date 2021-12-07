from app.db.db import User
from app.models import (
    LoginCredentials,
    RegisterCredentials,
    RegisterResponse,
    BaseResponse,
    GardenCredentials,
    GardenBase,
)
from app.core.handlers import (
    upload_garden_data,
    get_user,
    check_garden,
    get_garden_data,
)
from app.core.exceptions import DataException
from fastapi import (
    Depends,
    FastAPI,
    HTTPException,
    Security,
    status,
)
from fastapi.exceptions import RequestValidationError
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.auth import Auth
from app.db.db import database
from starlette.responses import JSONResponse
from fastapi import Request
from fastapi.logger import logger as fastapi_logger
import logging

security = HTTPBearer()
auth_handler = Auth()

app = FastAPI(
    title="Smart Garden",
    contact={
        "name": "Medvedev Ivan",
        "email": "gjo5br@inf.elte.hu",
    },
    license_info={
        "name": "Apache 2.0",
        "url": "https://www.apache.org/licenses/LICENSE-2.0.html",
    },
)

logger = logging.getLogger("gunicorn.error")
fastapi_logger.handlers = logger.handlers
fastapi_logger.setLevel(logger.level)

tags_metadata = [
    {
        "name": "API methods",
        "description": "Methods for authorization/registration of users in the API",
    },
    {
        "name": "items",
        "description": "Manage items. So _fancy_ they have their own docs.",
        "externalDocs": {
            "description": "Items external docs",
            "url": "https://fastapi.tiangolo.com/",
        },
    },
]


@app.exception_handler(DataException)
async def exception_handler(request: Request, exc: DataException):
    return JSONResponse(
        status_code=422,
        content={"success": False, "message": exc.error},
    )


@app.post("/api/users/login", tags=["User methods"])
async def login(user_data: LoginCredentials):
    user = await get_user(user_data.email)
    if user is None:
        return HTTPException(status_code=401, detail="Invalid username")
    if not auth_handler.verify_password(user_data.password, user.password):
        return HTTPException(status_code=401, detail="Invalid password")

    access_token = auth_handler.encode_token(user.email)
    refresh_token = auth_handler.encode_refresh_token(user.email)
    return {"access_token": access_token, "refresh_token": refresh_token}


@app.post("/api/users/register", tags=["User methods"], response_model=RegisterResponse)
async def signup(user_data: RegisterCredentials):
    logger.info(user_data)
    user = await get_user(user_data.email)
    if user:
        raise HTTPException(
            status_code=409,
            detail="This login is already exists",
            headers={"WWW-Authenticate": "Bearer"},
        )
    await User.objects.create(
        email=user_data.email,
        password=auth_handler.encode_password(user_data.password),
        full_name=user_data.full_name,
    )

    return {"success": True}


@app.post("/api/garden/token", tags=["Garden methods"])
async def get_token_for_garden(garden_data: GardenBase):
    if await check_garden(garden_data.garden_id):
        access_token = auth_handler.encode_garden_token(garden_id=garden_data.garden_id)
    else:
        return HTTPException(status_code=401, detail="Invalid Garden")

    return {"access_token": access_token}


def register_exception(app: FastAPI):
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request, exc: RequestValidationError
    ):

        exc_str = f"{exc}".replace("\n", " ").replace("   ", " ")
        # or logger.error(f'{exc}')
        logger.error(request, exc_str)
        content = {"status_code": 10422, "message": exc_str, "data": None}
        return JSONResponse(
            content=content, status_code=status.HTTP_422_UNPROCESSABLE_ENTITY
        )


@app.get(
    "/api/garden/data/{garden_id}",
    # response_model=GardenCredentials,
    tags=["Garden methods"],
)
async def get_garden(
    garden_id: int,
    # credentials: HTTPAuthorizationCredentials = Security(security),
):
    garden = await get_garden_data(garden_id)
    if not garden:
        return HTTPException(status_code=401, detail="Invalid Garden")
    fastapi_logger.info(garden)
    return garden
    # token = credentials.credentials
    # fastapi_logger.info(token)
    # if auth_handler.decode_garden_token(token):
    #     response, error = await upload_garden_data(garden_data)
    #     if not response:
    #         raise DataException(error=error)
    #     return {"success": True}


@app.post(
    "/api/garden/data",
    response_model=BaseResponse,
    tags=["Garden methods"],
)
async def put_garden_data(
    garden_data: GardenCredentials,
    credentials: HTTPAuthorizationCredentials = Security(security),
):
    token = credentials.credentials
    if auth_handler.decode_garden_token(token):
        response, error = await upload_garden_data(garden_data)
        if not response:
            raise DataException(error=error)
        return {"success": True}


@app.on_event("startup")
async def startup() -> None:
    if not database.is_connected:
        await database.connect()


@app.on_event("shutdown")
async def shutdown() -> None:
    if database.is_connected:
        await database.disconnect()
