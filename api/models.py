from django.db import models
from jsonfield import JSONField
from django.template.defaultfilters import slugify
from .face_encoding import FaceEncoding
from django.contrib.auth.models import User

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



