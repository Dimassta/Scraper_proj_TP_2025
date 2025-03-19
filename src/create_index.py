from elasticsearch import Elasticsearch
import warnings

warnings.filterwarnings("ignore", category=UserWarning, module="elasticsearch")

es = Elasticsearch("http://localhost:9200")

# Удаляем старый индекс (для тестирования)
es.indices.delete(index="warha_news_index", ignore_unavailable=True)

index_body = {
    "settings": {
        "analysis": {
            "tokenizer": {
                "ngram_tokenizer": {
                    "type": "ngram",
                    "min_gram": 3,
                    "max_gram": 4,
                    "token_chars": ["letter", "digit"]
                },
                "hashtag_tokenizer": {
                    "type": "pattern",
                    "pattern": "(#\\w+)",
                    "group": 1
                }
            },
            "filter": {
                "russian_stop": {
                    "type": "stop",
                    "stopwords_path": "analysis/stopwords/stopwords.txt"  # 1. Путь должен быть относительным внутри контейнера
                },
                "synonym_filter": {
                    "type": "synonym",
                    "synonyms_path": "analysis/synonyms/synonyms.txt",    # 2. Добавлены параметры безопасности
                    "lenient": True
                },
                "edge_ngram_filter": {
                    "type": "edge_ngram",                                 # 3. Исправлен порядок применения
                    "min_gram": 2,
                    "max_gram": 5
                },
                "russian_stemmer": {
                    "type": "stemmer",
                    "language": "russian"
                }
            },
            "analyzer": {
                "warhammer_analyzer": {
                    "type": "custom",
                    "tokenizer": "ngram_tokenizer",
                    "filter": [                                           # 4. Изменен порядок фильтров
                        "lowercase",
                        "russian_stop",
                        "synonym_filter",
                        "edge_ngram_filter",                              # 5. Ngram после синонимов
                        "russian_stemmer"
                    ]
                },
                "hashtag_analyzer": {
                    "type": "custom",
                    "tokenizer": "hashtag_tokenizer",
                    "filter": [
                        "lowercase",
                        "asciifolding"
                    ]
                }
            }
        }
    },
    "mappings": {
        "properties": {
            "title": {
                "type": "text",
                "analyzer": "warhammer_analyzer",
                "fields": {
                    "keyword": {"type": "keyword"}
                }
            },
            "author": {"type": "keyword"},
            "link": {"type": "keyword"},
            "tags": {
                "type": "text",
                "analyzer": "hashtag_analyzer",
                "fields": {
                    "keyword": {"type": "keyword"}
                }
            },
            "structured_content": {
                "type": "nested",
                "properties": {
                    "header": {
                        "type": "text",
                        "analyzer": "warhammer_analyzer"
                    },
                    "text": {
                        "type": "text",
                        "analyzer": "warhammer_analyzer"
                    }
                }
            }
        }
    }
}

es.indices.create(index="warha_news_index", body=index_body)
print("Индекс успешно создан")