import hashlib
import json
import logging
from dataclasses import dataclass
from decimal import Decimal
from urllib.parse import urlparse, urlunparse

import httpx
from bs4 import BeautifulSoup
from fastapi import HTTPException

from app.services import media as media_service

logger = logging.getLogger(__name__)

_BROWSER_UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
)
_SUPPORTED_CURRENCIES = {"UAH", "USD", "EUR", "GBP"}
_FETCH_TIMEOUT = 10.0
_MAX_BODY_BYTES = 2 * 1024 * 1024
_CACHE_TTL = 3600
_FRANKFURTER_URL = "https://api.frankfurter.app/latest"


@dataclass
class RawParsed:
    title: str | None
    description: str | None
    image_url: str | None
    price: Decimal | None
    currency: str | None


@dataclass
class ParsedItemData:
    title: str | None
    description: str | None
    image_url: str | None
    image_width: int | None
    image_height: int | None
    price: Decimal | None
    currency: str | None
    product_url: str


def _normalize_url(url: str) -> str:
    parsed = urlparse(url.strip())
    normalized = parsed._replace(
        scheme=parsed.scheme.lower(),
        netloc=parsed.netloc.lower(),
        path=parsed.path.rstrip("/") or "/",
    )
    return urlunparse(normalized)


def _cache_key(url: str) -> str:
    digest = hashlib.sha256(_normalize_url(url).encode()).hexdigest()
    return f"url_parse:{digest}"


async def _fetch_html(url: str) -> str:
    async with httpx.AsyncClient(follow_redirects=True) as client:
        async with client.stream(
            "GET",
            url,
            timeout=_FETCH_TIMEOUT,
            headers={"User-Agent": _BROWSER_UA},
        ) as response:
            response.raise_for_status()
            content_type = response.headers.get("content-type", "")
            if "text/html" not in content_type:
                raise ValueError("not_html")
            chunks: list[bytes] = []
            total = 0
            async for chunk in response.aiter_bytes(chunk_size=8192):
                total += len(chunk)
                if total > _MAX_BODY_BYTES:
                    break
                chunks.append(chunk)
            return b"".join(chunks).decode("utf-8", errors="replace")


def _og(soup: BeautifulSoup, prop: str) -> str | None:
    tag = soup.find("meta", property=prop)
    if tag and tag.get("content"):
        return str(tag["content"]).strip() or None
    return None


def _meta_name(soup: BeautifulSoup, name: str) -> str | None:
    tag = soup.find("meta", attrs={"name": name})
    if tag and tag.get("content"):
        return str(tag["content"]).strip() or None
    return None


def _jsonld_price(soup: BeautifulSoup) -> tuple[str | None, str | None]:
    for script in soup.find_all("script", type="application/ld+json"):
        try:
            data = json.loads(script.string or "")
            nodes = data if isinstance(data, list) else [data]
            for node in nodes:
                if node.get("@type") == "Product":
                    offers = node.get("offers", {})
                    if isinstance(offers, list):
                        offers = offers[0] if offers else {}
                    price = offers.get("price")
                    currency = offers.get("priceCurrency")
                    if price is not None:
                        return str(price), currency
        except (json.JSONDecodeError, AttributeError, TypeError):
            continue
    return None, None


def _extract_fields(html: str) -> RawParsed:
    soup = BeautifulSoup(html, "html.parser")

    title = (
        _og(soup, "og:title")
        or _meta_name(soup, "title")
        or (soup.title.string.strip() if soup.title and soup.title.string else None)
    )
    description = _og(soup, "og:description") or _meta_name(soup, "description")
    image_url = _og(soup, "og:image")

    raw_price = _og(soup, "og:price:amount")
    raw_currency = _og(soup, "og:price:currency")
    if raw_price is None:
        raw_price, raw_currency = _jsonld_price(soup)

    price: Decimal | None = None
    if raw_price is not None:
        try:
            price = Decimal(str(raw_price).replace(",", "."))
        except Exception:
            price = None

    return RawParsed(
        title=title,
        description=description,
        image_url=image_url,
        price=price,
        currency=raw_currency.upper() if raw_currency else None,
    )


async def _download_image(url: str) -> tuple[bytes, str] | None:
    try:
        async with httpx.AsyncClient(follow_redirects=True) as client:
            resp = await client.get(url, timeout=10.0, headers={"User-Agent": _BROWSER_UA})
            resp.raise_for_status()
            content_type = resp.headers.get("content-type", "image/jpeg")
            return resp.content, content_type
    except Exception:
        return None


async def _convert_currency(price: Decimal, from_currency: str) -> tuple[Decimal, str]:
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                _FRANKFURTER_URL,
                params={"from": from_currency, "to": "UAH"},
                timeout=5.0,
            )
            resp.raise_for_status()
            rate = Decimal(str(resp.json()["rates"]["UAH"]))
            return (price * rate).quantize(Decimal("0.01")), "UAH"
    except Exception:
        logger.warning("Currency conversion failed for %s → UAH", from_currency)
        return price, from_currency


async def _enrich(raw: RawParsed, product_url: str) -> ParsedItemData:
    currency = raw.currency or "UAH"
    price = raw.price
    if price is not None and currency not in _SUPPORTED_CURRENCIES:
        price, currency = await _convert_currency(price, currency)

    cloudinary_url: str | None = None
    image_width: int | None = None
    image_height: int | None = None

    if raw.image_url:
        result = await _download_image(raw.image_url)
        if result is not None:
            image_bytes, content_type = result
            try:
                cloudinary_url, image_width, image_height = await media_service.upload_image(
                    image_bytes, content_type, "items"
                )
            except Exception:
                logger.warning("Cloudinary upload failed for image from %s", product_url)

    return ParsedItemData(
        title=raw.title,
        description=raw.description,
        image_url=cloudinary_url,
        image_width=image_width,
        image_height=image_height,
        price=price,
        currency=currency,
        product_url=product_url,
    )


async def parse_url(url: str, redis) -> ParsedItemData:
    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https"):
        raise HTTPException(
            status_code=400,
            detail={"error": {"code": "INVALID_URL", "message": "URL must use http or https scheme."}},
        )

    key = _cache_key(url)

    if redis is not None:
        try:
            cached = await redis.get(key)
            if cached:
                data = json.loads(cached)
                return ParsedItemData(
                    title=data["title"],
                    description=data["description"],
                    image_url=data["image_url"],
                    image_width=data.get("image_width"),
                    image_height=data.get("image_height"),
                    price=Decimal(data["price"]) if data["price"] is not None else None,
                    currency=data["currency"],
                    product_url=data["product_url"],
                )
        except Exception:
            pass

    try:
        html = await _fetch_html(url)
    except httpx.TimeoutException:
        raise HTTPException(
            status_code=422,
            detail={"error": {"code": "FETCH_FAILED", "message": "Request to the URL timed out."}},
        )
    except httpx.HTTPStatusError as exc:
        raise HTTPException(
            status_code=422,
            detail={"error": {"code": "FETCH_FAILED", "message": f"URL returned status {exc.response.status_code}."}},
        )
    except ValueError as exc:
        if str(exc) == "not_html":
            raise HTTPException(
                status_code=422,
                detail={"error": {"code": "NOT_HTML", "message": "URL does not point to an HTML page."}},
            )
        raise HTTPException(
            status_code=422,
            detail={"error": {"code": "FETCH_FAILED", "message": "Failed to fetch the URL."}},
        )
    except Exception:
        raise HTTPException(
            status_code=422,
            detail={"error": {"code": "FETCH_FAILED", "message": "Failed to fetch the URL."}},
        )

    raw = _extract_fields(html)
    result = await _enrich(raw, url)

    if redis is not None:
        try:
            cache_payload = {
                "title": result.title,
                "description": result.description,
                "image_url": result.image_url,
                "image_width": result.image_width,
                "image_height": result.image_height,
                "price": str(result.price) if result.price is not None else None,
                "currency": result.currency,
                "product_url": result.product_url,
            }
            await redis.set(key, json.dumps(cache_payload), ex=_CACHE_TTL)
        except Exception:
            pass

    return result
