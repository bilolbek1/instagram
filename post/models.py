from django.contrib.auth import get_user_model
from django.core.validators import FileExtensionValidator, MaxLengthValidator
from django.db import models
from django.db.models import UniqueConstraint

from shared.models import BaseModel
# Create your models here.

User = get_user_model()

class Post(BaseModel):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    image = models.ImageField(upload_to='post_photos/',
        validators=[FileExtensionValidator(allowed_extensions=['jpeg', 'jpg', 'png', ])])
    caption = models.TextField(validators=[MaxLengthValidator(2000)])

    class Meta:
        db_table = 'posts'
        verbose_name = 'post'
        verbose_name_plural = 'posts'


class PostComment(BaseModel):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    comment = models.TextField()
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        related_name='child',
        null=True,
        blank=True
    )




class PostLike(BaseModel):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='likes')

    class Meta:
        constraints =[
            UniqueConstraint(fields=['author', 'post'], name='postLikeUnique')
        ]



class CommentLike(BaseModel):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    comment = models.ForeignKey(PostComment, on_delete=models.CASCADE, related_name='likes')

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=['author', 'comment'],
                name='CommentLikeUnique'
            )
        ]




















































