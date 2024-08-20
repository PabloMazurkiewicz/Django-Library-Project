from django.db import models
from django.contrib.auth.models import User
from datetime import date
from typing import Optional


class Author(models.Model):
    name: str = models.CharField(max_length=100, db_index=True)
    ratings_count: Optional[int] = models.IntegerField(null=True, blank=True, db_index=True)
    average_rating: Optional[float] = models.FloatField(null=True, blank=True, db_index=True)
    about: Optional[str] = models.TextField()

    def __str__(self) -> str:
        return self.name


class Book(models.Model):
    title: str = models.CharField(max_length=200, db_index=True)
    description: Optional[str] = models.TextField()
    author: Author = models.ForeignKey(Author, related_name='books', on_delete=models.CASCADE)
    publication_date: Optional[date] = models.DateField(default=date.today, null=True, blank=True, db_index=True)
    average_rating: Optional[float] = models.FloatField(null=True, blank=True, db_index=True)
    ratings_count: Optional[int] = models.IntegerField(null=True, blank=True, db_index=True)

    def __str__(self) -> str:
        return self.title


class Favorite(models.Model):
    user: User = models.ForeignKey(User, related_name='favorites', on_delete=models.CASCADE)
    book: Book = models.ForeignKey(Book, related_name='favorites', on_delete=models.CASCADE)

    class Meta:
        unique_together = ('user', 'book')

    def __str__(self) -> str:
        return f"Favorite: {self.user.username} - {self.book.title}"
