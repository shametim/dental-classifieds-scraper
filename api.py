import asyncio
import json
import urllib.parse
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup

app = FastAPI()


async def capture_screenshot(url):
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.goto(url)
        await page.wait_for_timeout(1000)  # Wait for 1 second to allow page to load
        url_parts = urllib.parse.urlparse(url)
        file_name = f"{url_parts.netloc}_{url_parts.path.replace('/', '_')}.jpg"
        await page.screenshot(path=file_name, full_page=True)
        await browser.close()
        return file_name


async def extract_classifieds(url):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto(url)
        await page.wait_for_timeout(1000)  # Wait for 1 second to allow page to load

        content = await page.content()
        soup = BeautifulSoup(content, "html.parser")

        classifieds = []
        for li in soup.select("ul.classifieds li"):
            title_elem = li.select_one(".title")
            description_elem = li.select_one(".text")
            contact_elem = li.find("a", href=lambda x: x and x.startswith("mailto:"))

            if title_elem and description_elem:
                classified = {
                    "title": title_elem.get_text(strip=True),
                    "description": description_elem.get_text(strip=True),
                    "contact": contact_elem.get("href").replace("mailto:", "")
                    if contact_elem
                    else None,
                }
                classifieds.append(classified)

        with open("classifieds.json", "w", encoding="utf-8") as f:
            json.dump(classifieds, f, ensure_ascii=False, indent=4)

        await browser.close()
        return "classifieds.json"


async def extract_links(url):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto(url)
        await page.wait_for_timeout(1000)  # Wait for 1 second to allow page to load

        content = await page.content()
        soup = BeautifulSoup(content, "html.parser")

        links = []
        base_url = (
            urllib.parse.urlparse(url).scheme
            + "://"
            + urllib.parse.urlparse(url).netloc
        )
        for a in soup.find_all("a", href=True):
            href = a["href"]
            if (
                not href.startswith("#")
                and not href.startswith("mailto:")
                and not urllib.parse.urlparse(href).netloc
            ):
                if href.startswith("/"):
                    href = base_url + href
                links.append(href)

        with open("outgoing_links.txt", "w", encoding="utf-8") as f:
            for i, link in enumerate(links, start=1):
                f.write(f"{i}. {link}\n")

        await browser.close()
        return "outgoing_links.txt"


@app.get("/screenshot/")
async def get_screenshot(url: str):
    try:
        file_name = await capture_screenshot(url)
        return FileResponse(file_name)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/classifieds/")
async def get_classifieds(url: str):
    try:
        file_name = await extract_classifieds(url)
        return FileResponse(file_name)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/links/")
async def get_links(url: str):
    try:
        file_name = await extract_links(url)
        return FileResponse(file_name)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
