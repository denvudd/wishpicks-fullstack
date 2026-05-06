import random
import uuid

_OTP_TTL = 600
_COOLDOWN_TTL = 60
_MAX_ATTEMPTS = 5


class OTPInvalidError(Exception):
    pass


class OTPMaxAttemptsError(Exception):
    pass


class OTPCooldownError(Exception):
    pass


async def generate_and_store_otp(redis, user_id: uuid.UUID) -> str:
    code = f"{random.randint(0, 999999):06d}"
    await redis.setex(f"email_otp:{user_id}", _OTP_TTL, code)
    await redis.delete(f"email_otp_attempts:{user_id}")
    return code


async def verify_otp(redis, user_id: uuid.UUID, code: str) -> None:
    otp_key = f"email_otp:{user_id}"
    attempts_key = f"email_otp_attempts:{user_id}"

    stored = await redis.get(otp_key)
    if stored is None:
        raise OTPInvalidError()

    attempts = await redis.incr(attempts_key)
    await redis.expire(attempts_key, _OTP_TTL)

    if stored == code:
        await redis.delete(otp_key, attempts_key)
        return

    if attempts >= _MAX_ATTEMPTS:
        await redis.delete(otp_key, attempts_key)
        raise OTPMaxAttemptsError()

    raise OTPInvalidError()


async def check_and_set_cooldown(redis, user_id: uuid.UUID) -> None:
    cooldown_key = f"email_otp_cooldown:{user_id}"
    existing = await redis.get(cooldown_key)
    if existing is not None:
        raise OTPCooldownError()
    await redis.setex(cooldown_key, _COOLDOWN_TTL, "1")
