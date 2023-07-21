from django.db import models
from userapp.models import CustomUser
import uuid
# Create your models here.


class Post(models.Model):
    id=models.UUIDField(default=uuid.uuid4,primary_key=True,editable=False,db_index=True)
    author=models.ForeignKey(CustomUser,on_delete=models.CASCADE,related_name='Post')
    title=models.TextField()
    content=models.TextField()
    images=models.BinaryField(null=True,blank=True)
    postedon=models.DateTimeField(auto_now_add=True,editable=False)
    updatedon=models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"{self.author.username} {self.postedon} {self.title}"