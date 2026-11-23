from django.shortcuts import render
from django.http import HttpResponse
from .models import Book
from django.db.models import Q
from django.db.models import Count, Sum, Avg, Max, Min
from .models import Book, Address, Student
from django.db.models import Count
from django.db.models import F, FloatField, ExpressionWrapper, Sum
from apps.bookmodule.models import Lab9Book
from apps.bookmodule.models import Publisher
from django.db.models import Sum
from django.db.models import OuterRef, Subquery




def index(request):
    name = request.GET.get("name") or "world!"
    return render(request, "bookmodule/index.html", {"name": name})

def index2(request, val1=0):
    return HttpResponse("value1 = " + str(val1))

def viewbook(request, bookId):
    book1 = {
        'id': 123,
        'title': 'Continuous Delivery',
        'author': 'J. Humble and D. Farley'
    }

    book2 = {
        'id': 456,
        'title': 'Secrets of Reverse Engineering',
        'author': 'E. Eilam'
    }

    targetBook = None

    if book1['id'] == bookId:
        targetBook = book1

    if book2['id'] == bookId:
        targetBook = book2

    context = {'book': targetBook}

    return render(request, 'bookmodule/show.html', context)

def index(request):
    return render(request, 'bookmodule/index.html')


def list_books(request):
    return render(request, 'bookmodule/list_books.html')


def viewbook(request, bookId):
    return render(request, 'bookmodule/one_book.html')


def aboutus(request):
    return render(request, 'bookmodule/aboutus.html')

def links(request):
    return render(request, 'bookmodule/links.html')

def formatting(request):
    return render(request, 'bookmodule/formatting.html')

def listing(request):
    return render(request, 'bookmodule/listing.html')

def tables(request):
    return render(request, 'bookmodule/tables.html')

def search_books(request):

    if request.method == "POST":

        string = request.POST.get('keyword', '').lower()

        isTitle = request.POST.get('option1')
        isAuthor = request.POST.get('option2')

        # now filter
        books = __getBooksList()
        newBooks = []

        for item in books:
            contained = False

            if isTitle and string in item['title'].lower():
                contained = True

            if not contained and isAuthor and string in item['author'].lower():
                contained = True

            if contained:
                newBooks.append(item)

        return render(
            request,
            'bookmodule/bookList.html',
            {'books': newBooks}
        )

    return render(request, 'bookmodule/search.html')

def __getBooksList():
    book1 = {
        'id': 12344321,
        'title': 'Continuous Delivery',
        'author': 'J.Humble and D. Farley'
    }

    book2 = {
        'id': 56788765,
        'title': 'Reversing: Secrets of Reverse Engineering',
        'author': 'E. Eilam'
    }

    book3 = {
        'id': 43211234,
        'title': 'The Hundred-Page Machine Learning Book',
        'author': 'Andriy Burkov'
    }

    return [book1, book2, book3]

def simple_query(request):
    mybooks = Book.objects.filter(title__icontains='and')
    return render(request,'bookmodule/bookList.html',{'books': mybooks}
    )

def complex_query(request):
    mybooks = Book.objects.filter(
        author__isnull=False
    ).filter(
        title__icontains='and'
    ).filter(
        edition__gte=2
    ).exclude(
        price__lte=100
    )[:10]

    if len(mybooks) >= 1:
        return render(request, 'bookmodule/bookList.html', {'books': mybooks})
    else:
        return render(request, 'bookmodule/index.html')

def lab8_task1(request):
    books = Book.objects.filter(Q(price__lte=80))

    return render(
        request,
        'bookmodule/bookList.html',
        {'books': books}
    )

def lab8_task2(request):
    books = Book.objects.filter(
        Q(edition__gt=3) &
        (Q(title__icontains='qu') | Q(author__icontains='qu'))
    )

    return render(
        request,
        'bookmodule/bookList.html',
        {'books': books}
    )

def lab8_task3(request):
    books = Book.objects.filter(
        ~Q(edition__gt=3) &
        (~Q(title__icontains='qu') | ~Q(author__icontains='qu'))
    )

    return render(
        request,
        'bookmodule/bookList.html',
        {'books': books}
    )

def lab8_task4(request):
    books = Book.objects.all().order_by('title')

    return render(
        request,
        'bookmodule/bookList.html',
        {'books': books}
    )

def lab8_task5(request):
    stats = Book.objects.aggregate(
        total_books=Count('id'),
        total_price=Sum('price'),
        average_price=Avg('price'),
        maximum_price=Max('price'),
        minimum_price=Min('price')
    )

    return render(
        request,
        'bookmodule/lab8_task5.html',
        {'stats': stats}
    )

def lab8_task7(request):
    cities = Address.objects.annotate(
        student_count=Count('student')
    ).order_by('city')

    return render(
        request,
        'bookmodule/lab8_task7.html',
        {'cities': cities}
    )
 

def lab9_task1(request):
    total_quantity = (
        Lab9Book.objects.aggregate(total=Sum("quantity"))["total"] or 0
    )

    if total_quantity == 0:
        return HttpResponse("No books available.")

    books = Lab9Book.objects.annotate(
        availability_percentage=ExpressionWrapper(
            F("quantity") * 100.0 / total_quantity,
            output_field=FloatField()
        )
    )

    result = "<h1>Lab 9 - Task 1</h1>"
    result += "<h2>Book Availability Percentage</h2>"

    for book in books:
        result += (
            f"<p>{book.title} - "
            f"Quantity: {book.quantity} - "
            f"Availability: {book.availability_percentage:.2f}%</p>"
        )

    return HttpResponse(result)




def lab9_task2(request):
    publishers = Publisher.objects.annotate(
        total_stock=Sum("lab9book__quantity")
    )

    result = "<h1>Lab 9 - Task 2</h1>"
    result += "<h2>Publishers and Total Book Stock</h2>"

    for publisher in publishers:
        total = publisher.total_stock or 0

        result += (
            f"<p>Publisher: {publisher.name} - "
            f"Total Stock: {total}</p>"
        )

    return HttpResponse(result)



def lab9_task3(request):
    oldest_book = Lab9Book.objects.filter(
        publisher=OuterRef("pk")
    ).order_by("pubdate")

    publishers = Publisher.objects.annotate(
        oldest_book_title=Subquery(
            oldest_book.values("title")[:1]
        ),
        oldest_book_date=Subquery(
            oldest_book.values("pubdate")[:1]
        )
    )

    result = "<h1>Lab 9 - Task 3</h1>"
    result += "<h2>Oldest Book for Each Publisher</h2>"

    for publisher in publishers:
        title = publisher.oldest_book_title or "No books"
        date = publisher.oldest_book_date

        result += (
            f"<p>Publisher: {publisher.name} - "
            f"Oldest Book: {title} - "
            f"Publication Date: {date}</p>"
        )

    return HttpResponse(result)


def lab9_task4(request):
    publishers = Publisher.objects.annotate(
        avg_price=Avg("lab9book__price"),
        min_price=Min("lab9book__price"),
        max_price=Max("lab9book__price")
    )

    result = "<h1>Lab 9 - Task 4</h1>"
    result += "<h2>Book Price Statistics for Each Publisher</h2>"

    for publisher in publishers:
        if publisher.avg_price is not None:
            result += (
                f"<p>Publisher: {publisher.name} - "
                f"Average Price: {publisher.avg_price:.2f} - "
                f"Minimum Price: {publisher.min_price:.2f} - "
                f"Maximum Price: {publisher.max_price:.2f}</p>"
            )
        else:
            result += f"<p>Publisher: {publisher.name} - No books</p>"

    return HttpResponse(result)


def lab9_task5(request):
    publishers = Publisher.objects.annotate(
        highly_rated_count=Count(
            "lab9book",
            filter=Q(lab9book__rating__gte=4)
        )
    )

    result = "<h1>Lab 9 - Task 5</h1>"
    result += "<h2>Highly Rated Books for Each Publisher</h2>"

    for publisher in publishers:
        result += (
            f"<h3>Publisher: {publisher.name}</h3>"
            f"<p>Highly Rated Books Count: "
            f"{publisher.highly_rated_count}</p>"
        )

        books = Lab9Book.objects.filter(
            publisher=publisher,
            rating__gte=4
        )

        for book in books:
            result += (
                f"<p>Book: {book.title} - "
                f"Quantity: {book.quantity} - "
                f"Rating: {book.rating}</p>"
            )

    return HttpResponse(result)
    

def lab9_task6(request):
    publishers = Publisher.objects.annotate(
        matching_books_count=Count(
            "lab9book",
            filter=Q(
                lab9book__price__gt=50,
                lab9book__quantity__range=(1, 4)
            )
        )
    )

    result = "<h1>Lab 9 - Task 6</h1>"
    result += "<h2>Books with Price > 50 and Quantity Between 1 and 4</h2>"

    for publisher in publishers:
        result += (
            f"<p>Publisher: {publisher.name} - "
            f"Matching Books Count: "
            f"{publisher.matching_books_count}</p>"
        )

    return HttpResponse(result)