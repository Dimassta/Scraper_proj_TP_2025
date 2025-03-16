from elasticsearch import Elasticsearch, helpers
import json


es = Elasticsearch("http://localhost:9200")


with open('warha_news_without_date.json', 'r', encoding='utf-8') as file:
    data = json.load(file)


actions = [
    {
        "_index": "warha_news_index",
        "_id": item["id"],
        "_source": item
    }
    for item in data
]


try:
    success, failed = helpers.bulk(es, actions, stats_only=False, raise_on_error=False)
    print(f"Успешно загружено: {success}")
    if failed:
        print(f"Ошибки при загрузке: {failed}")
        for error in failed:
            print(f"Ошибка в документе {error['index']['_id']}: {error['index']['error']}")
except Exception as e:
    print(f"Ошибка: {e}")