import json

# Загрузка данных из JSON-файла
with open('warha_news_with_id.json', 'r', encoding='utf-8') as file:
    data = json.load(file)

# Удаление поля date из каждого элемента
for item in data:
    if 'date' in item:
        del item['date']

# Сохранение обновлённых данных в новый файл
with open('warha_news_without_date.json', 'w', encoding='utf-8') as file:
    json.dump(data, file, ensure_ascii=False, indent=4)

print("Поле 'date' удалено. Результат сохранён в warha_news_without_date.json")