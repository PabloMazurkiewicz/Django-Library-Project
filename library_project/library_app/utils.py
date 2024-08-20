import zipfile
import json
from io import TextIOWrapper
from .models import Author, Book

def load_data_from_zip(zip_path):
    with zipfile.ZipFile(zip_path, 'r') as z:
        author_file = None
        book_file = None

        for file_info in z.infolist():
            if 'authors.json' in file_info.filename:
                author_file = file_info
            if 'books.json' in file_info.filename:
                book_file = file_info

        if not author_file or not book_file:
            raise FileNotFoundError("Could not find authors.json or books.json in the zip file.")

        with z.open(author_file) as f:
            authors = json.load(TextIOWrapper(f))
            author_map = {}
            for author_data in authors:
                author, created = Author.objects.get_or_create(
                    name=author_data['name'],
                    defaults={
                        'bio': author_data.get('about', ''),
                        'average_rating': author_data.get('average_rating', None),
                        'ratings_count': author_data.get('ratings_count', None)
                    }
                )
                author_map[author_data['id']] = author

        with z.open(book_file) as f:
            books = json.load(TextIOWrapper(f))
            for book_data in books:
                author_id = book_data['author_id']
                author = author_map.get(author_id)
                if author:
                    Book.objects.create(
                        title=book_data['title'],
                        description=book_data.get('description', ''),
                        author=author,
                        publication_date=book_data.get('publication_date', None),
                        average_rating=book_data.get('average_rating', None),
                        ratings_count=book_data.get('ratings_count', None)
                    )
