from django.shortcuts import render
from rest_framework import generics
from rest_framework_simplejwt.authentication import JWTAuthentication
from .models import Post
from .serializers import PostSerializer
from .permissions import PostsPermission, PostObjectPermission, TimelinePermission
from followers.models import Follower
from friendships.models import Friendship

# Create your views here.


class PostView(generics.ListCreateAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [PostsPermission]

    queryset = Post.objects.all()
    serializer_class = PostSerializer

    def get_queryset(self):
        posts = Post.objects.filter(private=False).order_by("created_at").reverse()

        return posts

    def perform_create(self, serializer):
        return serializer.save(published_by=self.request.user)


class PostDetailView(generics.DestroyAPIView, generics.UpdateAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [PostsPermission, PostObjectPermission]

    queryset = Post.objects.all()
    serializer_class = PostSerializer


class TimelineView(generics.ListAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [TimelinePermission]

    queryset = Post.objects.all()
    serializer_class = PostSerializer

    def get_queryset(self):
        followers = Follower.objects.filter(user_following_id=self.request.user.id)

        friendships = Friendship.objects.filter(user_requesting_id=self.request.user.id)

        posts = []
        for follow in followers:
            find_posts = Post.objects.filter(published_by=follow.user_followed_id)
            for post in find_posts:
                posts.append(post)

        for friend in friendships:
            if friend.status == "accepted":
                find_posts = Post.objects.filter(published_by=friend.user_receiving_id)
                for post in find_posts:
                    posts.append(post)

        posts.sort(key=lambda x: x.created_at, reverse=True)

        return posts
