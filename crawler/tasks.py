import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
import os
from django.conf import settings
from dotenv import load_dotenv
from api.models import Recipe
from celery import shared_task
from urllib.request import urlretrieve
load_dotenv(settings.BASE_DIR+"/dev.env")
HOME_URL = os.environ.get('HOME_URL')

@shared_task
def crawler_worker():


    home_source = requests.get(HOME_URL).text
    home_page = BeautifulSoup(home_source, 'lxml')


    info = home_page.find('div', class_='resultList justify three')
    list_recipe_id=Recipe.objects.values_list('id', flat=True)
    id_info = {}
    for img in info.find_all('div', class_='box'):

        # img_url
        img_url = img.img['data-src']

        # print(img_url)

        receipe_url = img.a['href']
        # print(receipe_url)
        receipe_source = requests.get(receipe_url).text
        receipe_page = BeautifulSoup(receipe_source, 'lxml')

        # Receipe_id
        food_id = receipe_page.find('div', class_='print')
        url = food_id.find('a').attrs['href']
        receipe_id = re.findall(r"\d+", url)[0]
        #只爬取尚未爬取過的
        if int(receipe_id) in list_recipe_id:
            print("duplicate,continue")
            continue
        # download img to media/recipe/
        img_dir = settings.MEDIA_ROOT + "/recipe/" + "%s.jpeg" % receipe_id
        urlretrieve(img_url, img_dir)
        print(img_dir)
        # Receipe_name
        food = receipe_page.find('div', class_='detailWood')
        food_name = food.find('div', class_='title')
        receipe_name = food_name.b.text
        # print(receipe_name)

        # cooking_time
        try:
            time = receipe_page.find('div', class_='timeLen')
            time_ = time.find_all('span')[1].text
            cooking_time = re.findall(r'\d+[\u4e00-\u9fff]+', time_)[0]

        except:
            cooking_time = None

        # dish_description
        try:
            description = receipe_page.find('div', class_='des')
            description = description.pre.text

        except:
            description = None

        # ingredient_table
        table_ = receipe_page.find_all('table')[0]
        df = pd.read_html(str(table_))[0]
        df_ = df.rename(index=str, columns={0: "ingredient", 1: "portion_size"})
        ingredient_table = df_
        receipe_table = {}
        ingredient = []
        portion = []
        for i in range(len(ingredient_table)):
            ingredient.append(ingredient_table.iloc[i, 0])
            portion.append(ingredient_table.iloc[i, 1])
        receipe_table = dict(zip(ingredient, portion))

        # step
        step_list = receipe_page.find('div', class_='stepList')
        my_list = []
        for step in step_list.find_all('pre'):
            my_list.append(step.text)

        cooking_step = {}
        keys = range(len(my_list))
        values = my_list
        for i in keys:
            cooking_step[i] = values[i]

        detail = {
            'name': receipe_name,
            'description': description,
            'img_url': img_url,
            'cooking_time': cooking_time,
            'ingredient_table': receipe_table,
            'cooking_steps': cooking_step
        }
        id_info[receipe_id] = detail
        r=Recipe(id=receipe_id,name=detail['name'],description=detail['description'],cooking_time=detail['cooking_time'],
                ingredient_table=detail['ingredient_table'],cooking_steps=detail['cooking_steps'],img_url="recipe/" + "%s.jpeg" % receipe_id)
        r.save()