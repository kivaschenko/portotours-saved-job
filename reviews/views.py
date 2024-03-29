from django.views.generic import DetailView, ListView

from reviews.models import Review


class ReviewDetailView(DetailView):
    model = Review
    template_name = 'reviews/review_details.html'
    queryset = Review.objects.all()
