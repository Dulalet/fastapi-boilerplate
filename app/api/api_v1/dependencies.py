import base64
import json
from uuid import UUID

from fastapi import HTTPException, Request


def get_user_uuid_from_headers(request: Request) -> UUID:
    try:
        userinfo = json.loads(base64.b64decode(request.headers.get("x-userinfo")))
        user_uuid = UUID(userinfo["id"])
    except TypeError:
        raise HTTPException(status_code=400, detail="Empty X-USERINFO Header")
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid UUID value")
    return user_uuid


def get_company_uuid_from_headers(request: Request) -> UUID:
    try:
        company_uuid = UUID(request.headers.get("x-company-id"))
    except TypeError:
        raise HTTPException(status_code=400, detail="Empty X-COMPANY-ID Header")
    except ValueError:
        raise HTTPException(status_code=400, detail="Not a valid UUID value")
    return company_uuid
