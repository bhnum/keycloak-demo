from typing import Annotated

from fastapi import Depends, HTTPException, Security, status
from fastapi.security import OAuth2AuthorizationCodeBearer
from keycloak import KeycloakOpenID
from pydantic import BaseModel

from app.config import settings


class User(BaseModel):
    id: str
    username: str
    email: str
    first_name: str
    last_name: str
    realm_roles: list[str]
    client_roles: list[str]


# This is used for fastapi docs authentification
oauth2_scheme = OAuth2AuthorizationCodeBearer(
    authorizationUrl=str(settings.AUTH_URL),  # https://sso.example.com/auth/
    tokenUrl=settings.auth_token_url,  # https://sso.example.com/auth/realms/example-realm/protocol/openid-connect/token
)

# This actually does the auth checks
# client_secret_key is not mandatory if the client is public on keycloak
keycloak_openid = KeycloakOpenID(
    server_url=settings.AUTH_URL,  # https://sso.example.com/auth/
    client_id=settings.AUTH_CLIENT_ID,  # backend-client-id
    client_secret_key=settings.AUTH_CLIENT_SECRET,  # your backend client secret
    realm_name=settings.AUTH_REALM,  # example-realm
)


def get_idp_public_key():
    return (
        "-----BEGIN PUBLIC KEY-----\n"
        f"{keycloak_openid.public_key()}"
        "\n-----END PUBLIC KEY-----"
    )


# Get the payload/token from keycloak
async def get_payload(token: Annotated[str, Security(oauth2_scheme)]) -> dict:
    try:
        return keycloak_openid.decode_token(
            token,
            key=get_idp_public_key(),
            options={"verify_signature": True, "verify_aud": False, "exp": True},
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),  # "Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


# Get user infos from the payload
async def get_current_user(payload: Annotated[dict, Depends(get_payload)]) -> User:
    try:
        return User(
            id=payload.get("sub"),
            username=payload.get("preferred_username"),
            email=payload.get("email"),
            first_name=payload.get("given_name"),
            last_name=payload.get("family_name"),
            realm_roles=payload.get("realm_access", {}).get("roles", []),
            client_roles=payload.get("realm_access", {}).get("roles", []),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),  # "Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
