from storages.backends.s3boto3 import S3Boto3Storage
from urllib.parse import urlparse, urlunparse

class MediaStorage(S3Boto3Storage):
    location = 'uploads'

    def url(self, name):
        url = super().url(name)
        # Check if the request is for a preview (e.g., contains a 'preview' query parameter)
        if 'preview' in name:
            return url

        # Otherwise, return a clean URL
        parsed_url = urlparse(url)
        clean_url = urlunparse((parsed_url.scheme, parsed_url.netloc, parsed_url.path, None, None, None))
        return clean_url
