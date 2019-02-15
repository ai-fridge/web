from django.db import models
from jsonfield import JSONField
from django.template.defaultfilters import slugify
from .face_encoding import FaceEncoding
from django.contrib.auth.models import User
from django.utils import timezone

# Create your models here.

#upload folder
upload_Memberfolder = 'image/'
upload_Recipefolder = 'recipe/'
#define rename function
def photo_path(instance, filename):
    basefilename, file_extension= os.path.splitext(filename)
    return 'images/{basename}{ext}'.format(basename= instance.user.id,ext= file_extension)
#create Member
class Member(models.Model):
    user =models.OneToOneField(User,on_delete=models.CASCADE)
    locale = models.CharField(max_length=10)
    slug = models.SlugField(max_length=200,unique=True,editable=False)
    avatar_encoding = JSONField(editable=False)
    # created_at = models.DateTimeField(editable=False)
    # updated_at = models.DateTimeField(editable=False)
    image_url = models.ImageField(upload_to=upload_Memberfolder,blank=True)
    def save(self,*args,**kwargs):
        """On save"""
        # create unique slug with name and id
        new = self.user.username+str(self.user.id)
        self.slug = slugify(new)
        self.avatar_encoding = FaceEncoding(self.image_url)
        # new_name= upload_folder+self.name+"."+str(self.image_url).split('.')[-1]
        # self.image_url =new_name
        return super(Member,self).save(*args,**kwargs)
    def __str__(self):
        return self.slug


class Recipe(models.Model):
    id=models.BigIntegerField(primary_key=True)
    name=models.CharField(max_length=200)
    description=models.CharField(max_length=200,null=True)
    img_url=models.ImageField(upload_to=upload_Recipefolder,null=True)
    cooking_time=models.CharField(max_length=20,null=True)
    ingredient_table=JSONField(null=True)
    cooking_steps=JSONField(null=True)
    def __str__(self):
        return self.id+'_'+self.name

class Food_Category(models.Model):
    id=models.BigIntegerField(primary_key=True)
    food_name=models.CharField(max_length=200)
    created_at = models.DateTimeField(editable=False)
    updated_at = models.DateTimeField(editable=False)
    def save(self, *args, **kwargs):
        ''' On save, update timestamps '''
        if not self.id:
            self.created_at = timezone.now()
        self.updated_at = timezone.now()
        return super(Food_Category, self).save(*args, **kwargs)
    def __str__(self):
        return self.food_name

class Member_Fridge(models.Model):
    id = models.BigIntegerField(primary_key=True)
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    food_category=models.ForeignKey(Food_Category,on_delete=models.CASCADE)
    food_qty=models.IntegerField()
    fridge_img_url=models.CharField(max_length=120)
    fridge_predict_img_url = models.CharField(max_length=120)
    created_at = models.DateTimeField(editable=False)
    updated_at = models.DateTimeField(editable=False)
    def save(self, *args, **kwargs):
        ''' On save, update timestamps '''
        if not self.id:
            self.created_at = timezone.now()
        self.updated_at = timezone.now()
        return super(Member_Fridge, self).save(*args, **kwargs)
    def __str__(self):
        return self.user