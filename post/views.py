from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Post, PostLike, PostComment, CommentLike
from rest_framework import generics, status
from .serializer import PostSerializer, PostLikeSerializer, CommentSerializer, CommentLikeSerializer
from rest_framework.permissions import IsAuthenticatedOrReadOnly, AllowAny, IsAuthenticated
from shared.custom_pagination import PostListPagination



# POSTLARNI CHIQARISH UCHUN YOZILGAN VIEW
class PostListApiView(generics.ListAPIView):
    serializer_class = PostSerializer
    permission_classes = [AllowAny, ]
    pagination_class = PostListPagination

    def get_queryset(self):
        return Post.objects.all()


# POST YARATISH UCHUN YOZILGAN VIEW
class PostCreateView(generics.CreateAPIView):
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated, ]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


# POSTNI TAHRIRLASH VA O'CHIRISH UCHUN YOZILGAN VIEW
class PostRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, ]

    def put(self, request, *args, **kwargs):
        post = self.get_object()
        serializer = self.serializer_class(post, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {
                'success': True,
                'code': status.HTTP_200_OK,
                'message': 'Post muvaffaqiyatli tarzda yangilandi',
                'data': serializer.data
            }
        )

    def delete(self, request, *args, **kwargs):
        post = self.get_object()
        post.delete()
        return Response(
            {
            'success': True,
            "code": status.HTTP_204_NO_CONTENT,
            'message': 'Post o\'chirildi'
            }
        )



# POST UCHUN YOZILGAN COMMENTARIYALARNI KO'RISH UCHUN YOZILGAN VIEW

class CommentListView(generics.ListAPIView):
    serializer_class = CommentSerializer
    permission_classes = [AllowAny, ]

    def get_queryset(self):
        post_id = self.kwargs['pk']
        queryset = PostComment.objects.filter(post__id=post_id)
        return queryset


# POSTGA COMMENTARIYA QOLDIRISH UCHUN YA'NI COMMENTARIYA YARATISH UCHUN YOZILGAN VIEW
class CreateCommentView(generics.CreateAPIView):
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated, ]

    def perform_create(self, serializer):
        post_id = self.kwargs['pk']
        serializer.save(author=self.request.user, post_id=post_id)



# POSTGA BOSILGAN LIKELARNI CHIQARISH

class PostLikeView(generics.ListAPIView):
    serializer_class = PostLikeSerializer
    permission_classes = [AllowAny, ]

    def get_queryset(self):
        post_id = self.kwargs['pk']
        return PostLike.objects.filter(post_id=post_id)


# COMMENTGA BOSILGAN LIKELARNI CHIQARISH

class CommentLikeView(generics.ListAPIView):
    serializer_class = CommentLikeSerializer
    permission_classes = [AllowAny, ]

    def get_queryset(self):
        comment_id = self.kwargs['pk']
        return CommentLike.objects.filter(comment_id=comment_id)


# AYNI 1TA COMMENTNI CHIQARISH

class CommentRetrieveView(generics.RetrieveAPIView):
    serializer_class = CommentSerializer
    permission_classes = [AllowAny, ]
    queryset = PostComment.objects.all()





# POSTGA LIKE BOSISH VA O'CHIRISH UCHUN VIEW

class PostClickLikeView(APIView):

    def post(self, request, pk):
        try:
            post_like = PostLike.objects.create(author=self.request.user, post_id=pk)
            serializer = PostLikeSerializer(post_like)
            data = {
                'success': True,
                "message": "Postga like bosildi",
                'data': serializer.data
            }
            return Response(data, status=status.HTTP_201_CREATED)
        except Exception as e:
            data = {
                'success': False,
                'message': str(e),
                'data': None
            }
            return Response(data, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        try:
            post_like = PostLike.objects.get(author=self.request.user, post_id=pk)
            post_like.delete()
            data = {
                'success': True,
                'message': 'Like o\'chirildi',
                "data": None
            }
            return Response(data, status=status.HTTP_204_NO_CONTENT)

        except Exception as e:
            data = {
                'success': False,
                'message': str(e),
                'data': None
            }
            return Response(data, status=status.HTTP_400_BAD_REQUEST)
























