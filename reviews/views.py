from django.views.generic import DetailView, ListView
from django.core.paginator import Paginator
from django.shortcuts import render
from django.http import JsonResponse
from .models import Review


class ReviewDetailView(DetailView):
    model = Review
    template_name = 'reviews/review_details.html'
    queryset = Review.objects.all()


class ReviewListView(ListView):
    model = Review
    template_name = 'reviews/review_list.html'
    context_object_name = 'reviews'

    def get_queryset(self):
        return super().get_queryset().filter(approved=True).order_by('-created_at')

    def render_to_response(self, context, **response_kwargs):
        # Get all reviews
        reviews = context['object_list']
        # Serialize reviews
        reviews_data = [{'id': review.id, 'rating': review.rating, 'title': review.title,
                         'short_text': review.short_text, 'full_name': review.full_name,
                         'created_at': review.created_at} for review in reviews]
        # Return JSON response
        return JsonResponse({'reviews': reviews_data}, **response_kwargs)


def review_list(request, experience_id):
    reviews = Review.objects.filter(approved=True, experience_id=experience_id).order_by('-created_at')
    paginator = Paginator(reviews, 10)  # Set the number of reviews per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    reviews_data = list(page_obj.object_list.values())  # Convert queryset to list of dictionaries

    data = {
        'reviews': reviews_data,
        'has_next': page_obj.has_next(),
        'has_previous': page_obj.has_previous(),
        'next_page_number': page_obj.next_page_number() if page_obj.has_next() else None,
        'previous_page_number': page_obj.previous_page_number() if page_obj.has_previous() else None,
        'total_pages': paginator.num_pages,
        'current_page_number': page_obj.number,
    }

    return JsonResponse(data)

