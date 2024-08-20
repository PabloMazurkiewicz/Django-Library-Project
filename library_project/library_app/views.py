import faiss
import numpy as np
from typing import Any, Dict, Optional
from django.http import HttpResponse, JsonResponse
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.views import APIView
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken
from rest_framework_simplejwt.views import TokenObtainPairView
from django.db.models import Q
from .models import Book, Author, Favorite
from .serializers import BookSerializer, AuthorSerializer, FavoriteSerializer, RegisterSerializer
from django.core.cache import cache

# Utility function to verify token
def verify_token(token_str: str) -> Optional[Dict[str, Any]]:
    try:
        token = AccessToken(token_str)
        return token.payload  # Returns the payload if token is valid
    except Exception as e:
        print(f"Token verification failed: {e}")
        return None

class CustomView(APIView):
    def get(self, request, format: Optional[str] = None) -> Response:
        auth_header = request.headers.get('Authorization')
        if auth_header:
            token_str = auth_header.split(' ')[1]  # Extract token from header
            payload = verify_token(token_str)

            if payload:
                return Response({"message": "Token is valid", "payload": payload})
            return Response({"message": "Invalid token"}, status=status.HTTP_401_UNAUTHORIZED)
        return Response({"message": "Authorization header missing"}, status=status.HTTP_400_BAD_REQUEST)

class BookList(generics.ListCreateAPIView):
    queryset = Book.objects.all()
    serializer_class = BookSerializer

    def get_queryset(self) -> Any:
        self.permission_classes = [AllowAny]
        queryset = super().get_queryset()
        search_query = self.request.GET.get('search', '')

        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query) | Q(author__name__icontains=search_query)
            )
        
        return queryset

    def get_permissions(self) -> Any:
        if self.request.method == 'POST':
            self.permission_classes = [IsAuthenticated]
        else:
            self.permission_classes = [AllowAny]
        return super().get_permissions()

    def perform_create(self, serializer: BookSerializer) -> None:
        serializer.save()

class BookDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    
    def get_permissions(self) -> Any:
        if self.request.method in ['PUT', 'DELETE']:
            self.permission_classes = [IsAuthenticated]
        else:
            self.permission_classes = [AllowAny]
        return super().get_permissions()

class AuthorList(generics.ListCreateAPIView):
    queryset = Author.objects.all()
    serializer_class = AuthorSerializer
    
    def get_permissions(self) -> Any:
        if self.request.method == 'POST':
            self.permission_classes = [IsAuthenticated]
        else:
            self.permission_classes = [AllowAny]
        return super().get_permissions()

    def perform_create(self, serializer: AuthorSerializer) -> None:
        serializer.save()

class AuthorDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Author.objects.all()
    serializer_class = AuthorSerializer

    def get_permissions(self) -> Any:
        if self.request.method in ['PUT', 'DELETE']:
            self.permission_classes = [IsAuthenticated]
        else:
            self.permission_classes = [AllowAny]
        return super().get_permissions()

class SearchBooks(APIView):
    def get(self, request, format: Optional[str] = None) -> Response:
        query = request.GET.get('search', '')
        if query:
            books = Book.objects.filter(Q(title__icontains=query) | Q(author__name__icontains=query))
        else:
            books = Book.objects.all()
        
        serializer = BookSerializer(books, many=True)
        return Response(serializer.data)

class AddFavorite(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, format: Optional[str] = None) -> Response:
        user = request.user
        book_id = request.data.get('book_id')
        
        try:
            book = Book.objects.get(id=book_id)
        except Book.DoesNotExist:
            return Response({"detail": "Book not found."}, status=status.HTTP_404_NOT_FOUND)
        
        favorite, created = Favorite.objects.get_or_create(user=user, book=book)
        if created:
            return Response(FavoriteSerializer(favorite).data, status=status.HTTP_201_CREATED)
        return Response({"detail": "This book is already in your favorites."}, status=status.HTTP_200_OK)

    def delete(self, request, format: Optional[str] = None) -> Response:
        user = request.user
        book_id = request.data.get('book_id')
        
        try:
            book = Book.objects.get(id=book_id)
        except Book.DoesNotExist:
            return Response({"detail": "Book not found."}, status=status.HTTP_404_NOT_FOUND)
        
        favorite = Favorite.objects.filter(user=user, book=book)
        if favorite.exists():
            favorite.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response({"detail": "This book is not in your favorites."}, status=status.HTTP_404_NOT_FOUND)

class Recommendation(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, format: Optional[str] = None) -> Response:
        user = request.user
        cache_key = f"recommendations_{user.id}"
        cached_recommendations = cache.get(cache_key)

        if cached_recommendations:
            return Response(cached_recommendations)

        favorites = user.favorites.all()
        favorite_books = [favorite.book for favorite in favorites]

        if not favorite_books:
            return Response({"message": "No favorite books found for recommendations."})

        all_books = Book.objects.exclude(id__in=[book.id for book in favorite_books])
        book_ids = [book.id for book in all_books]
        book_features = np.array([[book.ratings_count, book.average_rating] for book in all_books], dtype='float32')

        d = book_features.shape[1]
        nlist = 100
        quantizer = faiss.IndexFlatL2(d)
        index = faiss.IndexIVFFlat(quantizer, d, nlist, faiss.METRIC_L2)

        index.train(book_features)
        index.add(book_features)

        assert index.is_trained

        k = 5
        favorite_features = np.array([[book.ratings_count, book.average_rating] for book in favorite_books], dtype='float32')
        distances, indices = index.search(favorite_features, k)

        recommended_books = []
        for i in range(len(favorite_books)):
            for j in indices[i]:
                recommended_books.append(all_books[j])

        recommended_books = list({book.id: book for book in recommended_books}.values())[:5]
        
        serializer = BookSerializer(recommended_books, many=True)
        cache.set(cache_key, serializer.data, timeout=60*60)
        return Response(serializer.data)
    
class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = RegisterSerializer

class CustomTokenObtainPairView(TokenObtainPairView):
    permission_classes = (AllowAny,)

def home(request) -> HttpResponse:
    return HttpResponse("Welcome to the Library API.")
