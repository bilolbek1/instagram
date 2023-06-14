from django.urls import path
from .views import PostListApiView, PostCreateView, PostRetrieveUpdateDestroyView, CommentListView, CreateCommentView
from .views import PostLikeView, CommentLikeView, CommentRetrieveView
urlpatterns = [
    path('', PostListApiView.as_view()),
    path('create/', PostCreateView.as_view()),
    path('<uuid:pk>/', PostRetrieveUpdateDestroyView.as_view()),
    path('<uuid:pk>/comments/', CommentListView.as_view()),
    path('<uuid:pk>/comments/create/', CreateCommentView.as_view()),
    path('<uuid:pk>/likes/', PostLikeView.as_view()),
    path('comments/<uuid:pk>/likes/', CommentLikeView.as_view()),
    path('comments/<uuid:pk>/', CommentRetrieveView.as_view()),
]