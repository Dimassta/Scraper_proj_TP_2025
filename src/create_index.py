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
                "hashtag_tokenizer": {
                    "type": "pattern",
                    "pattern": "(#\\w+)",
                    "group": 1
                }
            },
            "filter": {
                "russian_stop": {
                    "type": "stop",
                    "stopwords_path": "analysis/stopwords/stopwords.txt"
                },
                "synonym_filter": {
                    "type": "synonym",
                    "synonyms_path": "analysis/synonyms/synonyms.txt",
                    "lenient": True,
                    "expand": False
                },
                "ru_stemmer": {
                    "type": "stemmer",
                    "language": "russian"
                },
                "edge_ngram_filter": {
                    "type": "edge_ngram",
                    "min_gram": 3,
                    "max_gram": 15
                }
            },
            "analyzer": {
                "warhammer_analyzer": {
                    "type": "custom",
                    "tokenizer": "standard",
                    "filter": [
                        "lowercase",
                        "russian_stop",
                        "synonym_filter",
                        "ru_stemmer",
                        "edge_ngram_filter"
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
                    "content": {
                        "type": "nested",
                        "properties": {
                            "text": {
                                "type": "text",
                                "analyzer": "warhammer_analyzer",
                                "term_vector": "with_positions_offsets"
                            }
                        }
                    }
                }
            }
        }
    }
}

es.indices.create(index="warha_news_index", body=index_body)
print("Индекс успешно создан")