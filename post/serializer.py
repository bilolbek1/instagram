from rest_framework import serializers

from post.models import PostLike, PostComment, CommentLike
from users.models import UserModel




class UserSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)

    class Meta:
        model = UserModel
        fields = ('id', 'username', 'photo')


# POST UCHUN YOZILGAN SERIALIZER
class PostSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    author = UserSerializer(read_only=True)
    post_likes_count = serializers.SerializerMethodField('get_post_likes_count')
    post_comments_count = serializers.SerializerMethodField('get_post_comments_count')
    me_liked = serializers.SerializerMethodField('get_me_liked')

    class Meta:
        model = UserModel
        fields = ('id', 'author', 'image', 'caption', 'post_comments_count', 'post_likes_count',
                  'created_time', 'me_liked')

    def get_post_likes_count(self, obj):
        return obj.likes.count()

    def get_post_comments_count(self, obj):
        return obj.comments.count()

    def get_me_liked(self,obj):
        request = self.context.get('request', None)
        if request and request.user.is_authenticated:
            try:
                like = PostLike.objects.filter(post=obj, author=request.user)
                return True
            except PostLike.DoesNotExist:
                return False
        return False





# COMMENTARIYA UCHUN YOZIGAN SERIALIZER
class CommentSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    author = UserSerializer(read_only=True)
    replies = serializers.SerializerMethodField('get_replies')
    me_liked = serializers.SerializerMethodField('get_me_liked')
    likes_count = serializers.SerializerMethodField('get_likes_count')

    class Meta:
        model = PostComment
        fields = ('id', 'author', 'replies', 'me_liked', 'likes_count', 'parent', 'comment',
                  'created_time', 'post')
        extra_kwargs = {'image': {"required": False}}


    def get_replies(self, obj):
        if obj.child.exists():
            serializers = self.__class__(obj.child.all(), many=True, context=self.context)
            return serializers.data
        else:
            return None

    def get_me_liked(self, obj):
        user = self.context.get('request').user
        if user.is_authenticated:
            return obj.likes.filter(author=user).exists()
        else:
            return False

    def get_likes_count(self, obj):
        return obj.likes.count()



# COMMENTARIYAGA LIKE QOLDIRISH UCHUN YOZILGAN SERIALIZER
class CommentLikeSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    author = UserSerializer(read_only=True)

    class Meta:
        model = CommentLike
        fields = ('id', 'author', 'comment')


# POSTGA LIKE QOLDIRISH UCHUN YOZILGAN SERIALIZER
class PostLikeSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    author = UserSerializer(read_only=True)

    class Meta:
        model = PostLike
        fields = ('id', 'author', 'post')



















































































































