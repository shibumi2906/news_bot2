#этот код должен работать , но не работает.
import requests
from bs4 import BeautifulSoup
from loguru import logger

# Настройка логирования
logger.add("logs/parser.log", format="{time} {level} {message}", level="DEBUG")


def fetch_news():
    """Получает последние 10 новостей с Mastodon"""
    url = "https://mastodon.social/explore/links"
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        logger.info(f"Отправка запроса на {url}")
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            logger.info("Запрос успешен, парсинг страницы...")
            soup = BeautifulSoup(response.content, "html.parser")

            # Логируем часть страницы для проверки структуры
            logger.debug(f"HTML содержимое: {soup.prettify()[:1000]}")

            # Попробуем найти элементы с классом "a.story__details__title"
            titles_elements = soup.select("a.story__details__title")[:10]

            if not titles_elements:
                logger.warning("Элементы с классом a.story__details__title не найдены. Пробуем другой способ.")
                # Альтернативные варианты, если основной не сработал
                titles_elements = soup.select("a.story__title")[:10]  # Пример альтернативного пути
                if not titles_elements:
                    logger.error("Элементы с заголовками не найдены. Возможно, структура страницы изменилась.")
                    return []

            # Извлекаем заголовки и ссылки
            titles = [title.get_text().strip() for title in titles_elements]
            links = [title['href'] for title in titles_elements if title.has_attr('href')]

            if titles and links:
                logger.info(f"Успешно получено {len(titles)} заголовков и ссылок.")
                for title, link in zip(titles, links):
                    logger.info(f"Новость: {title}, Ссылка: {link}")
            else:
                logger.warning("Заголовки или ссылки не найдены на странице.")

            return list(zip(titles, links))
        else:
            logger.error(f"Ошибка при запросе: статус код {response.status_code}")
            return []
    except Exception as e:
        logger.exception(f"Произошла ошибка при парсинге новостей: {e}")
        return []
