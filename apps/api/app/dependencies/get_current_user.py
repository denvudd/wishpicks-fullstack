from fastapi import HTTPException, status

# TODO: replace with real JWT cookie validation in Phase 1


async def get_current_user():
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail={"error": {"code": "NOT_AUTHENTICATED", "message": "Authentication required."}},
    )


async def optional_current_user():
    return None
