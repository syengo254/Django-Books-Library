import datetime
from django.shortcuts import render, get_object_or_404
from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.urls import reverse, reverse_lazy
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required, permission_required
from django.views.generic.edit import CreateView, UpdateView, DeleteView

from .forms import RenewBookForm

from .models import Author, Book, BookInstance, Genre

# Create your views here.

def index(request):
    num_books = Book.objects.all().count()
    num_instances = BookInstance.objects.all().count()
    num_instances_available = BookInstance.objects.filter(status__exact='a').count()
    num_authors = Author.objects.count()
    genres = Genre.objects.all()
    num_visits = request.session.get('num_visits', 0)
    request.session['num_visits'] = num_visits + 1

    context = {
        'num_books': num_books,
        'num_instances': num_instances,
        'num_instances_available': num_instances_available,
        'num_authors': num_authors,
        'genres': genres,
        'num_visits': num_visits,
    }

    return render(request, 'index.html', context=context)



class BookListView(generic.ListView):
    model = Book
    context_object_name = 'books'
    template_name = 'books/list.html'
    paginate_by = 10 # afterwards just add get param on route e.g. books/?page=2


class BookDetailView(generic.DetailView):
    model = Book
    template_name = 'books/book_detail.html'


class AuthorListView(generic.ListView):
    model = Author
    template_name = 'authors/list.html'
    paginate_by = 10
    context_object_name = 'authors'



class AuthorDetailView(generic.DetailView):
    model = Author
    template_name = 'authors/author_detail.html'
    context_object_name = 'author'
    pk_url_kwarg = 'id'



class LoanedBooksByUserListView(LoginRequiredMixin, generic.ListView):
    """Generic class-based view listing books on loan to current user."""
    model = BookInstance
    template_name = 'instances/user_borrowed_list.html'
    paginate_by = 10

    def get_queryset(self):
        return BookInstance.objects.filter(borrower=self.request.user).filter(status__exact='o').order_by('due_back')



class AllLoanedBooksListView(PermissionRequiredMixin, generic.ListView):
    """This view will display all borrowed books to staff users only"""
    permission_required = 'catalog.can_mark_returned'
    model = BookInstance
    template_name = 'instances/librarian_borrowed_list.html'

    def get_queryset(self):
        return BookInstance.objects.all().order_by('due_back')



@login_required
@permission_required('catalog.can_mark_returned', raise_exception=True)
def renew_book_librarian(request, pk):
    book_instance = get_object_or_404(BookInstance, pk=pk)

    if request.method == 'POST':
        form  =  RenewBookForm(request.POST)

        if form.is_valid():
            book_instance.due_back = form.cleaned_data['renewal_date']
            book_instance.save()

            return HttpResponseRedirect(reverse('borrowed'))
        else:
            context = {
                'form': form,
                'book_instance': book_instance,
            }
            return render(request, 'instances/book_renew_librarian.html', context)
    
    else:
        proposed_renewal_date = datetime.date.today() + datetime.timedelta(weeks=3)
        form = RenewBookForm(initial={'renewal_date': proposed_renewal_date})

        context = {
            'form': form,
            'book_instance': book_instance,
        }

        return render(request, 'instances/book_renew_librarian.html', context)




class AuthorCreate(PermissionRequiredMixin, CreateView):
    model = Author
    fields = ['first_name', 'last_name', 'date_of_birth', 'date_of_death']
    initial = {'date_of_death': '11/06/2022'}
    template_name = 'authors/author_form.html'
    permission_required = 'catalog.can_mark_returned'


class AuthorUpdate(UpdateView):
    model = Author
    fields = '__all__' #not recommended for security incase you add new fields to model that are sensitive
    template_name = 'authors/author_form.html'



class AuthorDelete(DeleteView):
    model = Author
    success_url = reverse_lazy('authors')
    template_name = 'authors/author_confirm_delete.html'



class BookCreate(CreateView):
    model = Book
    fields = ['title', 'author', 'summary', 'isbn', 'genre', 'language',]
    initial = {'language': 'English'}
    template_name = 'books/book_form.html'


class BookUpdate(UpdateView):
    model = Book
    fields = '__all__'
    template_name = 'books/book_form.html'


class BookDelete(DeleteView):
    model = Book
    success_url = reverse_lazy('books')
    template_name = 'books/book_confirm_delete.html'
