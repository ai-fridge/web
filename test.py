import mysql.connector
import json

# connect mysql
conn = mysql.connector.connect(
    user='root',
    password='dj2133',
    host='localhost',
    database='test_login')

cur = conn.cursor()

# 執行sql語句
query = ("INSERT INTO api_recipe(id,name,description,img_url,cooking_time,ingredient_table,cooking_steps) values (%s,%s,%s,%s,%s,%s,%s)")

# 執行insert
with open('./receipe.json') as f:
    data = json.load(f)
for keys,values in data.items():
    id=keys
    name=values['name']
    description=values['description']
    img_url=values['img_url']
    cooking_time=values['cooking_time']
    ingredient_table=json.dumps(values['ingredient_table'])
    cooking_steps=json.dumps(values['cooking_steps'])
    try:
        cur.execute(query,[id,name,description,img_url,cooking_time,ingredient_table,cooking_steps])
        conn.commit()
    except:
        pass

#結束insert
cur.close()
conn.close()

# with open('./receipe.json') as f:
#     data = json.load(f)
# print(json.dumps(data).items())
#
# for k ,v in data.items():
#     print(k,type(v['name']),type(v['description']),type(v['img_url']),type(v['ingredient_table']))
# query = ("SELECT id,ingredient_table,cooking_steps FROM api_recipe")
# cur.execute(query)
#
# for id,ingredient_table,cooking_steps in cur:
#     print(id,type(id),json.loads(ingredient_table),json.loads(cooking_steps))