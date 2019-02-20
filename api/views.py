import os
import uuid
import json
import numpy as np
from django.shortcuts import render
from api.forms import UserForm,UserProfileInfoForm
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from api.models import Member,Food_Category,Member_Fridge,Recipe
from django.http import JsonResponse
from core.image import (convert_and_save, create_dir_folder, getBase64Str,
                          is_base64_image)

from yolo.predict import _main_
from django.views.decorators.csrf import csrf_exempt
import numpy as np
from django.contrib.auth.models import User
from django.utils import timezone
from django.conf import settings
from .face_encoding import detect_faces_in_image
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
####set up parameter####
media_root=settings.MEDIA_ROOT
config_path=settings.BASE_DIR+'/config.json'
ori_dirname=media_root+'/base64/'
yolo_output_path=media_root+'/yolo/'
########################



def index(request):
    return render(request,'api/index.html')
@login_required
def special(request):
    return HttpResponse("You are logged in !")
@login_required
def user_logout(request):
    logout(request)
    return HttpResponseRedirect(reverse('index'))

def register(request):
    registered = False
    if request.method == 'POST':
        user_form = UserForm(data=request.POST)
        profile_form = UserProfileInfoForm(data=request.POST)
        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save()
            user.set_password(user.password)
            user.save()
            profile = profile_form.save(commit=False)
            profile.user = user
            # if 'image_url' in request.FILES:
            #     print('found it')
            profile.image_url = request.FILES.get('image_url')
            profile.save()
            registered = True
        else:
            print(user_form.errors,profile_form.errors)
    else:
        user_form = UserForm()
        profile_form = UserProfileInfoForm()
    return render(request,'api/registration.html',
                          {'user_form':user_form,
                           'profile_form':profile_form,
                           'registered':registered})
def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)
        if user:
            if user.is_active:
                login(request,user)
                return HttpResponseRedirect(reverse('index'))
            else:
                return HttpResponse("Your account was inactive.")
        else:
            print("Someone tried to login and failed.")
            print("They used username: {} and password: {}".format(username,password))
            return HttpResponse("Invalid login details given")
    else:
        return render(request, 'api/login.html', {})
@login_required()
def detail(request):
    list_detail = Member.objects.filter(user=request.user)  # 把資料庫中對應user的資料全部撈出來
    context ={"list_detail":list_detail}
    return render(request, 'upload_profile/detail.html', context)

@login_required()
def my_account(request):
    account = Member.objects.filter(user_id=request.user.id).first()
    context = {"account": account}
    return render(request, 'my_account.html', context)

@login_required()
def My_Fridge(request):
    data = Member_Fridge.objects.filter(user=request.user.id)#.values('food_qty')
    jsondata ={}
    food_list = []

    for item in data:
        food_list.append({"id":item.food_category.id,"food_name":item.food_category.food_name,
                          "fridge_predict_img_url": item.fridge_predict_img_url,
                                   "food_qty":item.food_qty,"created_at":item.created_at,"updated_at":item.updated_at})
    jsondata['foods']=food_list
    return render(request, 'fridge.html', jsondata)

@login_required()
def Recommandation(request):
    data = Member_Fridge.objects.filter(user=request.user.id)  # .values('food_qty')
    food_list = []
    mapping={"milk":"牛奶","guava":"芭樂","cabbage":"高麗菜"}
    for item in data:
        food_list.append(mapping[item.food_category.food_name])
    data_r = Recipe.objects.all()
    recipe_dict={}
    for item in data_r:
        ingred = item.ingredient_table
        recipe_dict[item.id]=''.join(ingred)

    recommand_id = []
    for food in food_list:
        for k,v in recipe_dict.items():
            if food in v:
                recommand_id.append(k)

    recommand=[]

    for rid in recommand_id:
        a=Recipe.objects.filter(pk=rid)
        for i in a:
            recommand.append({"id":i.id,"name":json.loads(json.dumps(i.name)),"description":json.loads(json.dumps(i.description))})
    jsondata={}
    jsondata['recommand']=recommand
    return render(request, 'recommand.html', jsondata)
    # return HttpResponse('shit')
def Recipe_detail(request,pk):
    data =Recipe.objects.filter(pk=pk)
    jsondata = {}
    recipe_detail = []
    for item in data:
        recipe_detail.append({"id":item.id,"name":item.name,
                              "description": item.description,
                              "img_url":item.img_url,"cooking_time":item.cooking_time,
                              "ingredient_table":json.loads(json.dumps(item.ingredient_table)),
                              "cooking_steps": json.loads(json.dumps(item.cooking_steps))})
    jsondata['recipe_detail'] = recipe_detail
    return render(request,'recipe_detail.html',jsondata)


@api_view(['POST'])
def verify_face_recognition(request):
    if request.method == 'POST':
        data = request.data

        if is_base64_image(data['file']):
            b64_string = getBase64Str(data['file'])
        else:
            return Response({"error": "base64 image format is not correct"}, status=status.HTTP_400_BAD_REQUEST)

        dirname = 'media/face_recognition/'
        filename = str(uuid.uuid1())

        if not os.path.exists(dirname):
            create_dir_folder(dirname)

        # Get face encodings for any faces in the uploaded image
        unknown_face_img = convert_and_save(b64_string, dirname, filename)

        known_faces = Member.objects.values_list('avatar_encoding', flat=True)
        known_face_names = Member.objects.values_list('slug', flat=True)
        user_ids = Member.objects.values_list('user_id', flat=True)
        known_face_encoding = []

        for known_face in known_faces:
            known_face_encoding.append(np.array(json.loads(known_face)))

        result = detect_faces_in_image(unknown_face_img, known_face_encoding, known_face_names, user_ids)

        return Response(result)


@api_view(['POST'])
def Object_Detection(request):
    if request.method == "POST":
        data = request.data

        id = int(data['user_id'])
        #save origin base64 and predicted image
        file = data['file']
        if is_base64_image(file):
            b64_string = getBase64Str(file)
        else:
            return JsonResponse({"error": "base64 image format is not correct"})

        if not os.path.exists(ori_dirname):
            create_dir_folder(ori_dirname)
        username = User.objects.get(id=id).username
        img_ori = convert_and_save(b64_string,ori_dirname, username)

        label_result, fridge_predict_img_url,waste= _main_(config_path=config_path,input_path=img_ori,output_path=yolo_output_path)
        print(waste)
        # calculate total inventory of in DB
        inventory = Member_Fridge.objects.all()
        inventories = {}
        for invent in inventory:
            # print(invent.food_category,type(invent.food_category),invent.food_category.id,type(invent.food_category.id))
            food_name = str(invent.food_category)
            if food_name not in inventories.keys():
                inventories[food_name] = int(invent.food_qty)
            else:
                inventories[food_name] += int(invent.food_qty)

        # calculate difference between inventories and label_result
        # part1: calculate food "vanished"
        diff={}
        for k in inventories.keys():
            if k not in label_result.keys():
                diff[k]=-1*int(inventories[k])
        #         food_category = Food_Category.objects.get(food_name=k)
        #         Member_Fridge.objects.filter(food_category=food_category,user=id).delete()
        #
        # part2: calculate diff of food still "existed"
        for k in label_result.keys():
            if k in inventories.keys():
                diff[k]=label_result[k]-inventories[k]
            else:
                diff[k]=label_result[k]
        # calculate updated inventory of in DB under corresponding "id"
        p_inventory = Member_Fridge.objects.filter(user=id)
        p_inventories = {}
        for invent in p_inventory:
            food_name = str(invent.food_category)
            if food_name not in p_inventories.keys():
                p_inventories[food_name] = int(invent.food_qty)
            else:
                p_inventories[food_name] += int(invent.food_qty)

        p_updates={}
        for k in diff.keys():
            if k in p_inventories.keys():
                p_updates[k]=diff[k]+p_inventories[k]
            else:
                p_updates[k]=diff[k]

        # update new inventory into db_Member_Fridge of under corresponding "id"
        for k in p_updates.keys():
            if k in p_inventories.keys():
                food_qty = int(p_updates[k])
                food_category = Food_Category.objects.get(food_name=k)
                user_id = User.objects.get(id=id)
                Member_Fridge_instance = Member_Fridge.objects.get(user=user_id, food_category=food_category)
                Member_Fridge_instance.food_qty = food_qty
                Member_Fridge_instance.save()
            else:
                food_qty = int(p_updates[k])
                food_category = Food_Category.objects.get(food_name=k)
                user_id = User.objects.get(id=id)
                mf = Member_Fridge(user=user_id, food_category=food_category, food_qty=food_qty, fridge_img_url=img_ori,
                                   fridge_predict_img_url=fridge_predict_img_url, created_at=timezone.now())
                mf.save()
        #response to IOT
        data = Member_Fridge.objects.filter(user=id)  # .values('food_qty')
        jsondata = {}
        # user info

        jsondata['user'] = {"id": id, "name":username}
        # food info
        food_list = []
        for item in data:
            food_list.append({"id": item.food_category.id, "food_name": item.food_category.food_name,
                              "food_qty": item.food_qty, "created_at": item.created_at, "updated_at": item.updated_at})
        jsondata['foods'] = food_list
        return JsonResponse(jsondata)
    return HttpResponse("It's not POST!!")