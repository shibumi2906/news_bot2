from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
from loguru import logger
import asyncio

# Настройка логирования
logger.add("logs/parser.log", format="{time} {level} {message}", level="DEBUG")

async def fetch_news():
    """Получает последние 10 новостей с Mastodon"""
    url = "https://mastodon.social/explore/links"
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            await page.goto(url)
            await page.wait_for_timeout(5000)  # Ждем 5 секунд для загрузки страницы

            # Извлекаем HTML и ищем элементы
            content = await page.content()
            soup = BeautifulSoup(content, "html.parser")
            titles_elements = soup.select("a.story__details__title")[:10]
            titles = [title.get_text().strip() for title in titles_elements]
            links = [title['href'] for title in titles_elements]

            await browser.close()

            if titles and links:
                logger.info(f"Успешно получено {len(titles)} заголовков и ссылок.")
                for title, link in zip(titles, links):
                    logger.info(f"Новость: {title}, Ссылка: {link}")
            else:
                logger.warning("Заголовки или ссылки не найдены на странице.")

            return list(zip(titles, links))

    except Exception as e:
        logger.exception(f"Произошла ошибка при парсинге новостей: {e}")
        return []

# Вызов функции для тестирования
if __name__ == "__main__":
    asyncio.run(fetch_news())
