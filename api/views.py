from django.shortcuts import render
from api.forms import UserForm,UserProfileInfoForm
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from api.models import Member,Food_Category,Member_Fridge
from django.core import serializers
from django.http import JsonResponse

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
def My_Fridge(request):
    data = Member_Fridge.objects.filter(user=request.user.id)#.values('food_qty')
    jsondata ={}
    #user info
    jsondata['user']={"id":request.user.id,"name":request.user.username}
    #food info
    food_list = []
    for item in data:
        food_list.append({"id":item.food_category.id,"food_name":item.food_category.food_name,
                                   "food_qty":item.food_qty,"created_at":item.created_at,"updated_at":item.updated_at})
    jsondata['food']=food_list
    return JsonResponse(jsondata)