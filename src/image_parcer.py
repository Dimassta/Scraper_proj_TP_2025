import json
import os
import requests
import hashlib
from PIL import Image
from io import BytesIO
from urllib.parse import urlparse
import argparse


def get_unique_filename(url, output_dir):
    """Генерирует уникальное имя файла на основе URL"""
    parsed = urlparse(url)
    base_name = os.path.basename(parsed.path)
    name, ext = os.path.splitext(base_name)
    if not ext:
        ext = '.jpg'

    hash_prefix = hashlib.md5(url.encode()).hexdigest()[:6]
    return os.path.join(output_dir, f"{hash_prefix}_{name}{ext}")


def is_image_large_enough(image_data, min_width=100, min_height=100):
    """Проверяет размер изображения"""
    try:
        with Image.open(BytesIO(image_data)) as img:
            return img.width >= min_width and img.height >= min_height
    except Exception as e:
        print(f"Ошибка проверки размера: {e}")
        return False


def download_image(url, output_dir, min_size):
    """Скачивает и сохраняет изображение с проверкой размера"""
    try:
        response = requests.get(url, stream=True, timeout=10)
        response.raise_for_status()

        # Читаем первые 1024 байт для проверки заголовков
        content = b"".join([chunk for chunk in response.iter_content(1024)])
        if not is_image_large_enough(content, *min_size):
            return None

        # Получаем уникальное имя файла
        filename = get_unique_filename(url, output_dir)

        # Проверяем существование файла
        if os.path.exists(filename):
            return None

        # Сохраняем полное изображение
        with open(filename, 'wb') as f:
            f.write(content)
            for chunk in response.iter_content(8192):
                f.write(chunk)

        return filename
    except Exception as e:
        print(f"Ошибка загрузки {url}: {e}")
        return None


def extract_image_urls(data):
    """Рекурсивно извлекает все URL изображений из структуры JSON"""
    urls = set()

    def recursive_extract(obj):
        if isinstance(obj, dict):
            for k, v in obj.items():
                if k == 'image_url' or k == 'images' or k == 'img':
                    if isinstance(v, str):
                        urls.add(v)
                    elif isinstance(v, list):
                        for item in v:
                            urls.add(item)
                else:
                    recursive_extract(v)
        elif isinstance(obj, list):
            for item in obj:
                recursive_extract(item)

    recursive_extract(data)
    return urls


def main(json_file, output_dir, min_width, min_height):
    os.makedirs(output_dir, exist_ok=True)

    print("Загрузка JSON файла...")
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    print("Извлечение URL изображений...")
    urls = extract_image_urls(data)
    print(f"Найдено уникальных URL: {len(urls)}")

    downloaded = 0
    for i, url in enumerate(urls, 1):
        print(f"Обработка [{i}/{len(urls)}]: {url}")
        if download_image(url, output_dir, (min_width, min_height)):
            downloaded += 1

    print(f"\nСкачано изображений: {downloaded}/{len(urls)}")
    print(f"Сохранено в: {os.path.abspath(output_dir)}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Скачивание изображений из JSON')
    parser.add_argument('json_file', help='Путь к JSON файлу')
    parser.add_argument('-o', '--output', default='downloaded_images', help='Выходная директория')
    parser.add_argument('--min_width', type=int, default=100, help='Минимальная ширина')
    parser.add_argument('--min_height', type=int, default=100, help='Минимальная высота')

    args = parser.parse_args()

    main(
        json_file=args.json_file,
        output_dir=args.output,
        min_width=args.min_width,
        min_height=args.min_height
    )