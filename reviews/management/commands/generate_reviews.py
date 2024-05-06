# In generate_reviews.py

import random
from faker import Faker
from django.core.management.base import BaseCommand
from reviews.models import Review
from products.models import Experience  # Assuming the Experience model exists in experiences app

fake = Faker()

class Command(BaseCommand):
    help = 'Generate random reviews'

    def add_arguments(self, parser):
        parser.add_argument('num_reviews', type=int, help='The number of reviews to generate')

    def handle(self, *args, **options):
        num_reviews = options['num_reviews']
        experience_ids = Experience.objects.values_list('id', flat=True)
        print('experience_ids:\n', experience_ids)

        self.stdout.write(self.style.SUCCESS(f'Generating {num_reviews} reviews...'))

        # Function to generate a random review
        def generate_review():
            experience_id = random.choice(experience_ids)
            print('chosen experience_id:', experience_id)
            rating = random.choice([1, 2, 3, 4, 5])
            full_name = fake.name()
            title = fake.sentence(nb_words=5)
            short_text = fake.paragraph(nb_sentences=3)

            review = Review.objects.create(
                experience_id=experience_id,
                rating=rating,
                full_name=full_name,
                title=title,
                short_text=short_text,
                approved=True
            )

            return review

        # Generate reviews
        for _ in range(num_reviews):
            generate_review()

        self.stdout.write(self.style.SUCCESS('Reviews generated successfully!'))
