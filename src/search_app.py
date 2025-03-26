from elasticsearch import Elasticsearch
import time
import os

def clear_screen():
    if os.name == 'nt':
        os.system('cls')
    else:
        os.system('clear')


es = Elasticsearch("http://localhost:9200")


PAGE_SIZE = 10

def search_news(query, page=1):
    start_time = time.time()

    search_body = {
        "query": {
            "bool": {
                "should": [
                    {
                        "multi_match": {
                            "query": query,
                            "fields": ["title^3", "author^2", "tags"],
                            "fuzziness": "AUTO",
                            "prefix_length": 2
                        }
                    },
                    {
                        "nested": {
                            "path": "structured_content",
                            "query": {
                                "match": {"structured_content.header": query}
                            }
                        }
                    },
                    {
                        "nested": {
                            "path": "structured_content.content",
                            "query": {
                                "match": {"structured_content.content.text": query}
                            }
                        }
                    }
                ]
            }
        },
        "highlight": {
            "fields": {
                "title": {"type": "plain"},
                "structured_content.header": {"type": "plain"},
                "structured_content.content.text": {
                    "type": "plain",
                    "fragment_size": 150,
                    "number_of_fragments": 3
                }
            },
            "pre_tags": ["<em>"],
            "post_tags": ["</em>"]
        }
    }

    response = es.search(
        index="warha_news_index",
        body=search_body,
        size=PAGE_SIZE,
        from_=(page - 1) * PAGE_SIZE
    )

    end_time = time.time()
    return response['hits']['hits'], response['hits']['total']['value'], end_time - start_time

def print_news(news, total, current_page):
    total_pages = (total + PAGE_SIZE - 1) // PAGE_SIZE
    print(f"\nНайдено всего: {total} (Страница {current_page} из {total_pages})")
    for article in news:
        print(f"\nЗаголовок: {article['_source']['title']}")
        print(f"Автор: {article['_source']['author']}")
        print(f"Ссылка: {article['_source']['link']}")

        # Обработка подсветки
        highlights = article.get('highlight', {})

        if 'title' in highlights:
            print(f"\nСовпадение в заголовке: {' '.join(highlights['title'])}")

        # Обработка nested-структур
        if 'structured_content.header' in highlights:
            print(f"\nСовпадения в подзаголовках:")
            for header in highlights['structured_content.header']:
                print(f"- {header}")

        if 'structured_content.content.text' in highlights:
            print(f"\nСовпадения в тексте:")
            for text in highlights['structured_content.content.text']:
                print(f"- {text}")

    #
        print(f"Рейтинг: {article['_score']}")
        print("*" * 40)

def search_menu(query):
    current_page = 1
    while True:
        clear_screen()
        news, total, execution_time = search_news(query, current_page)
        print_news(news, total, current_page)
        print(f"\nВремя выполнения запроса: {execution_time:.4f} секунд")

        print("\nВыберите действие:")
        print("1 - Назад")
        print("2 - Далее")
        print("3 - Ввести страницу")
        print("4 - Выйти в меню")

        choice = input("Ваш выбор: ")

        if choice == "1":  # Назад
            if current_page > 1:
                current_page -= 1
            else:
                print("Вы уже на первой странице.")
                time.sleep(1)
        elif choice == "2":
            total_pages = (total + PAGE_SIZE - 1) // PAGE_SIZE
            if current_page < total_pages:
                current_page += 1
            else:
                print("Вы уже на последней странице.")
                time.sleep(1)
        elif choice == "3":
            total_pages = (total + PAGE_SIZE - 1) // PAGE_SIZE
            try:
                page = int(input(f"Введите номер страницы (от 1 до {total_pages}): "))
                if 1 <= page <= total_pages:
                    current_page = page
                else:
                    print("Некорректный номер страницы.")
                    time.sleep(1)
            except ValueError:
                print("Введите число.")
                time.sleep(1)
        elif choice == "4":
            break
        else:
            print("Неверный выбор. Попробуйте снова.")
            time.sleep(1)

def main():
    while True:
        clear_screen()
        print("Выберите действие:")
        print("1 - Поиск новостей")
        print("2 - Выйти")

        choice = input("Ваш выбор: ")

        if choice == "1":
            query = input("Введите запрос для поиска: ")
            search_menu(query)
        elif choice == "2":
            print("Выход из приложения.")
            break
        else:
            print("Неверный выбор. Попробуйте снова.")
            time.sleep(1)

if __name__ == "__main__":
    main()