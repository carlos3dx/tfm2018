import json
import re

import pymysql.cursors

with open('config.json') as json_data_file:
    config = json.load(json_data_file)
    config_categories = config.get("categories")

query_categories = "SELECT cat_title FROM category WHERE cat_title like %s AND cat_pages BETWEEN %s AND %s "

skip_categories = config_categories.get("ignore_with_name", {})
skip_categories_with_text = config_categories.get("ignore_with_text", {})

p_year = re.compile(r'\d{4}')
p_only_number = re.compile(r'^\d+$')
p_decade_ish = re.compile(r'^\d+(th|s|nd|rd)')


def obtain_categories(host, db, user, passwd, min=5, max=5000, lang_code="en"):
    connection = pymysql.connect(host, user, passwd, db, charset='utf8mb4', cursorclass=pymysql.cursors.DictCursor)

    categories = set()
    try:
        with connection.cursor() as cursor:
            cursor.execute(query_categories, ["%", min, max])
            for row in cursor.fetchall():
                category = row.get("cat_title").decode("utf-8")
                if permitted_category(category):
                    categories.add(category.replace("_", " "))
    finally:
        connection.close()

    return categories


def permitted_category(category):
    reply = True
    for skip_text in skip_categories_with_text:
        if skip_text.lower() in category.lower():
            reply = False
            break
    if reply and category in skip_categories:
        reply = False
    elif reply and re.search(p_only_number, category):
        reply = False
    elif reply and re.search(p_year, category):
        reply = False
    elif reply and re.search(p_decade_ish, category):
        reply = False

    return reply
