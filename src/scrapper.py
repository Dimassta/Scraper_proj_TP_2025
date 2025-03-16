import time
import json
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup

chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")


driver = webdriver.Chrome(options=chrome_options)

# Функция для загрузки существующих данных из JSON
def load_existing_data(filename):
    if os.path.exists(filename):
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

# Функция для сохранения данных в JSON
def save_data_to_json(data, filename):
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# Функция для сбора данных с главной страницы
def scrape_main_page(url):
    driver.get(url)
    time.sleep(5)  # Ожидание загрузки страницы

    soup = BeautifulSoup(driver.page_source, 'html.parser')
    news_blocks = soup.find_all('a', class_='news-div')  # Блоки с новостями

    news_data = []

    for block in news_blocks:
        try:
            # Заголовок
            title = block.find('div', class_='news-title').text.strip()

            # Ссылка на новость
            link = block['href']

            # Дата публикации
            date = block.find('div', class_='news-date').text.strip()

            # Изображение
            image_url = block.find('img')['src']

            # Сбор данных
            news_data.append({
                'title': title,
                'link': link,
                'date': date,
                'image_url': image_url
            })
        except Exception as e:
            print(f"Ошибка при обработке блока новости: {e}")

    return news_data

# Функция для сбора данных с страницы новости
def scrape_news_page(url):
    driver.get(url)
    time.sleep(5)  # Ожидание загрузки страницы

    soup = BeautifulSoup(driver.page_source, 'html.parser')

    # Заголовок
    title = soup.find('h1').text.strip() if soup.find('h1') else "Без заголовка"

    # Основной блок с текстом новости
    page_div = soup.find('div', class_='page-div')
    if not page_div:
        return None

    # Сбор структурированного контента
    structured_content = []
    current_header = None
    current_text = ""
    current_images = []

    for element in page_div.find_all(['h2', 'h3', 'h4', 'p', 'img']):
        if element.name in ['h2', 'h3', 'h4']:
            # Если есть текущий заголовок, сохраняем его с содержимым
            if current_header:
                structured_content.append({
                    'header': current_header['header'],
                    'content': current_header['content']
                })
            # Начинаем новый блок с заголовком
            current_header = {
                'header': element.text.strip(),
                'content': []
            }
            current_text = ""
            current_images = []
        elif element.name == 'p':
            # Добавляем текст к текущему блоку
            if current_header:
                current_header['content'].append({
                    'text': element.text.strip(),
                    'images': []
                })
            else:
                current_text += element.text.strip() + "\n"
        elif element.name == 'img':
            # Добавляем изображение к текущему блоку
            img_url = element.get('src')
            if img_url and not any(exclude in img_url for exclude in ["/img/avatar/", "/img/site/", "/img/forum/"]):
                if current_header:
                    current_header['content'][-1]['images'].append(img_url)
                else:
                    current_images.append(img_url)

    # Сохраняем последний блок (если есть)
    if current_header:
        structured_content.append({
            'header': current_header['header'],
            'content': current_header['content']
        })
    elif current_text.strip() or current_images:
        structured_content.append({
            'text': current_text.strip(),
            'images': current_images
        })

    # Дата, автор и теги
    tags_block = soup.find('div', class_='tags')
    if tags_block:
        # Дата
        date = tags_block.find('span', class_='a-nrm').text.strip()

        # Автор
        author = tags_block.find('a', class_='a-nrm').text.strip()

        # Теги
        tags = [tag.text.strip() for tag in tags_block.find_all('a', class_='a-tag')]
    else:
        date, author, tags = None, None, []

    # Лайки
    like_dislike_block = soup.find('div', class_='post_like_dislike_box')
    if like_dislike_block:
        likes = like_dislike_block.find('span', class_='like_dislike_count').text.strip()
    else:
        likes = None

    # Количество комментариев
    comments_block = soup.find('h3', string=lambda x: x and "Комментарии" in x)
    if comments_block:
        try:
            comments_count = comments_block.text.strip().split('(')[1].split(')')[0]
        except IndexError:
            comments_count = "0"
    else:
        comments_count = "0"

    return {
        'title': title,
        'structured_content': structured_content,
        'date': date,
        'author': author,
        'tags': tags,
        'likes': likes,
        'comments_count': comments_count
    }

# Основная функция
def scrape_warha():
    start_time = time.time()

    # Список всех страниц с новостями
    pages = ["https://warha.ru/"] + [f"https://warha.ru/page/{i}/" for i in range(2, 21)]

    # Загружаем существующие данные (если файл уже есть)
    filename = 'warha_news.json'
    existing_data = load_existing_data(filename)
    existing_links = {news['link'] for news in existing_data}

    total_images = 0
    total_news = 0

    # Сбор данных со всех страниц
    for page_url in pages:
        print(f"Скрапинг страницы: {page_url}")
        news_data = scrape_main_page(page_url)

        # Сбор данных с каждой новости
        for news in news_data:
            link = news['link']
            if link and link not in existing_links:  # Пропускаем уже обработанные новости
                print(f"Scraping {link}...")
                try:
                    news_details = scrape_news_page(link)
                    if news_details:
                        news.update(news_details)
                        # Подсчёт изображений
                        for block in news_details.get('structured_content', []):
                            if 'content' in block:
                                for item in block['content']:
                                    total_images += len(item.get('images', []))
                            else:
                                total_images += len(block.get('images', []))
                        total_news += 1

                        # Добавляем новую новость в существующие данные
                        existing_data.append(news)
                        # Сохраняем данные после каждой новости
                        save_data_to_json(existing_data, filename)
                except Exception as e:
                    print(f"Ошибка при обработке страницы {link}: {e}")

    # Статистика
    elapsed_time = time.time() - start_time
    print("\n--- Статистика ---")
    print(f"Обработано новостей: {total_news}")
    print(f"Найдено изображений: {total_images}")
    print(f"Затраченное время: {elapsed_time:.2f} секунд")

# Запуск скрапинга
scrape_warha()

# Закрытие драйвера
driver.quit()