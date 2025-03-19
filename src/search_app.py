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

# def search_news(query, page=1):
#     start_time = time.time()
#     search_body = {
#         "query": {
#             "bool": {
#                 "should": [
#                     {
#                         "multi_match": {
#                             "query": query,
#                             "fields": ["title", "author", "tags"]
#                         }
#                     },
#                     {
#                         "nested": {
#                             "path": "structured_content",
#                             "query": {
#                                 "multi_match": {
#                                     "query": query,
#                                     "fields": ["structured_content.header", "structured_content.content.text"]
#                                 }
#                             }
#                         }
#                     }
#                 ]
#             }
#         },
#         "highlight": {
#             "fields": {
#                 "title": {},
#                 "structured_content.header": {},
#                 "structured_content.content.text": {}
#             },
#             "pre_tags": ["**"],
#             "post_tags": ["**"]
#         }
#     }
#
#     response = es.search(index="warha_news_index", body=search_body)
#     end_time = time.time()
#     execution_time = end_time - start_time
#     return response['hits']['hits'], response['hits']['total']['value'], execution_time

def search_news(query, page=1):
    start_time = time.time()

    # Обработка хэштегов
    if query.startswith("#"):
        search_body = hashtag_search(query)
    else:
        search_body = general_search(query)

    response = es.search(index="warha_news_index", body=search_body)
    end_time = time.time()
    return response['hits']['hits'], response['hits']['total']['value'], end_time - start_time


def hashtag_search(query):
    clean_query = query[1:].strip().lower()
    return {
        "query": {
            "bool": {
                "should": [
                    {
                        "term": {
                            "tags.keyword": {  # Точное совпадение
                                "value": clean_query,
                                "boost": 2.0
                            }
                        }
                    },
                    {
                        "match": {  # Поиск по токенам
                            "tags": {
                                "query": clean_query,
                                "analyzer": "hashtag_analyzer"
                            }
                        }
                    }
                ]
            }
        },
        "highlight": {
            "fields": {"tags": {}}
        }
    }

def general_search(query):
    return {
        "query": {
            "bool": {
                "should": [
                    {
                        "multi_match": {
                            "query": query,
                            "fields": ["title^3", "author^2"]
                        }
                    },
                    {
                        "nested": {
                            "path": "structured_content",
                            "query": {
                                "multi_match": {
                                    "query": query,
                                    "fields": ["structured_content.header", "structured_content.text"]
                                }
                            }
                        }
                    }
                ]
            }
        },
        "highlight": {
            "fields": {
                "title": {},
                "structured_content.header": {},
                "structured_content.text": {}
            }
        }
    }

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
    # for article in news:
    #     print(f"\nЗаголовок: {article['_source']['title']}")
    #     print(f"Автор: {article['_source']['author']}")
    #     #print(f"Дата: {article['_source']['date']}")
    #     print(f"Ссылка: {article['_source']['link']}")
    #
    #     # Вывод подсвеченного текста
    #     if 'highlight' in article:
    #         if 'title' in article['highlight']:
    #             print(f"Совпадение в заголовке: {article['highlight']['title'][0]}")
    #         if 'structured_content.content.text' in article['highlight']:
    #             print(f"Совпадение в тексте: {article['highlight']['structured_content.content.text'][0]}")
    #
        print(f"Рейтинг: {article['_score']}")
        print("-" * 40)

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