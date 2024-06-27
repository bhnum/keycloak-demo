from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi_keycloak import OIDCUser, UsernamePassword

from app.auth import idp

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.get("/current_user", tags=["example-user-request"])
def protected(user: Annotated[OIDCUser, Depends(idp.get_current_user())]):
    return user


@router.get("/current_user/roles", tags=["example-user-request"])
def get_current_users_roles(user: Annotated[OIDCUser, Depends(idp.get_current_user())]):
    return user.roles


@router.get("/login", tags=["example-user-request"])
def login(user: UsernamePassword):
    return idp.user_login(
        username=user.username, password=user.password.get_secret_value()
    )


@router.get("/login-link", tags=["auth-flow"])
def login_redirect():
    return idp.login_uri


@router.get("/callback", tags=["auth-flow"])
def callback(session_state: str, code: str):
    return idp.exchange_authorization_code(session_state=session_state, code=code)


@router.get("/logout", tags=["auth-flow"])
def logout():
    return idp.logout_uri
