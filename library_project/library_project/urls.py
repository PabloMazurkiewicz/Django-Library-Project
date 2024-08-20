"""
URL configuration for library_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from library_app.views import BookList, BookDetail, AuthorList, AuthorDetail, SearchBooks, AddFavorite, Recommendation, RegisterView, home, CustomView

urlpatterns = [
    path('admin', admin.site.urls),
    path('books', BookList.as_view(), name='book-list'),
    path('books/<int:pk>', BookDetail.as_view(), name='book-detail'),
    path('authors', AuthorList.as_view(), name='author-list'),
    path('authors/<int:pk>', AuthorDetail.as_view(), name='author-detail'),
    path('favorites', AddFavorite.as_view(), name='add-favorite'),
    path('recommendations', Recommendation.as_view(), name='recommendation'),
    path('register', RegisterView.as_view(), name='register'),
    path('login', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/verify', CustomView.as_view(), name='token_verify'),
    path('', home, name='home'),  # Root URL pattern
]
