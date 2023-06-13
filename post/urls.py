from django.urls import path
from .views import PostListApiView, PostCreateView, PostRetrieveUpdateDestroyView, CommentListView, CreateCommentView

urlpatterns = [
    path('', PostListApiView.as_view()),
    path('create/', PostCreateView.as_view()),
    path('<uuid:pk>/', PostRetrieveUpdateDestroyView.as_view()),
    path('<uuid:pk>/comments/', CommentListView.as_view()),
    path('<uuid:pk>/comments/create/', CreateCommentView.as_view()),
]