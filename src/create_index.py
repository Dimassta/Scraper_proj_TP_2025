from elasticsearch import Elasticsearch
import warnings


warnings.filterwarnings("ignore", category=UserWarning, module="elasticsearch")

es = Elasticsearch("http://localhost:9200")


es.indices.delete(index="warha_news_index", ignore_unavailable=True)


# index_body = {
#     "mappings": {
#         "properties": {
#             "title": {"type": "text", "analyzer": "russian"},
#             "author": {"type": "text"},
#             "tags": {"type": "keyword"},
#             "structured_content": {
#                 "type": "nested",
#                 "properties": {
#                     "header": {"type": "text", "analyzer": "russian"},
#                     "content": {
#                         "type": "nested",
#                         "properties": {
#                             "text": {"type": "text", "analyzer": "russian"},
#                             "images": {"type": "keyword"}
#                         }
#                     }
#                 }
#             },
#             "link": {"type": "keyword"}
#         }
#     },
#     "settings": {
#         "analysis": {
#             "analyzer": {
#                 "russian": {
#                     "type": "custom",
#                     "tokenizer": "standard",
#                     "filter": ["lowercase"]
#                 }
#             }
#         }
#     }
# }

index_body = {
    "mappings": {
        "properties": {
            "title": {
                "type": "text",
                "analyzer": "warhammer_analyzer",
                "fields": {
                    "english": {
                        "type": "text",
                        "analyzer": "english"
                    }
                }
            },
            "author": {"type": "text"},
            "tags": {"type": "keyword"},
            "structured_content": {
                "type": "nested",
                "properties": {
                    "header": {
                        "type": "text",
                        "analyzer": "warhammer_analyzer",
                        "fields": {
                            "raw": {"type": "keyword"}
                        }
                    },
                    "content": {
                        "type": "nested",
                        "properties": {
                            "text": {
                                "type": "text",
                                "analyzer": "warhammer_analyzer",
                                "fields": {
                                    "exact": {"type": "keyword"}
                                }
                            }
                        }
                    }
                }
            },
            "link": {"type": "keyword"}
        }
    },
    "settings": {
        "analysis": {
            "filter": {
                # "multilingual_stop": {
                #     "type": "stop",
                #     "stopwords_path": "stopwords.txt",
                #     "ignore_case": True
                # },
                "english_stemmer": {
                    "type": "stemmer",
                    "language": "english"
                },
                "russian_stemmer": {
                    "type": "stemmer",
                    "language": "russian"
                }
                # "my_synonyms": {
                #     "type": "synonym",
                #     "synonyms_path": "synonyms.txt",
                #     "tokenizer": "whitespace"
                # }
            },
            "analyzer": {
                "warhammer_analyzer": {
                    "type": "custom",
                    "tokenizer": "standard",
                    "filter": [
                        "lowercase",
                        #"multilingual_stop",
                        #"my_synonyms",
                        "english_stemmer",
                        "russian_stemmer"
                    ]
                }
            }
        }
    }
}


es.indices.create(index="warha_news_index", body=index_body)
print("Индекс успешно создан")