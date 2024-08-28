# Set your secret key. Remember to switch to your live secret key in production.
# See your keys here: https://dashboard.stripe.com/apikeys
# See how to customize docs here: https://stripe.com/docs/connect/creating-a-payments-page
import stripe
from django.conf import settings
stripe.api_key = settings.STRIPE_SECRET_KEY

# stripe.Account.modify(
#   "{{CONNECTED_STRIPE_ACCOUNT_ID}}",
#   settings={
#     "branding": {
#       "icon": "file_123",
#       "logo": "file_456",
#       "primary_color": "#663399",
#       "secondary_color": "#4BB543",
#     },
#   },
# )