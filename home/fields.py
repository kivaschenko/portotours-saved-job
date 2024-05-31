from django.core.exceptions import ValidationError
from django.db.models.fields.files import ImageField, ImageFieldFile
from PIL import Image
import os


class SVGAndImageFieldFile(ImageFieldFile):
    def save(self, name, content, save=True):
        # Check if the file is an SVG
        if content.name.endswith('.svg') and content.content_type == 'image/svg+xml':
            self.name = name
            self.file = content
            self._committed = True
            if save:
                self.instance.save()
        else:
            super().save(name, content, save)

    def delete(self, save=True):
        if self.name.endswith('.svg'):
            # Deleting SVG files
            self.storage.delete(self.name)
            self._committed = False
            if save:
                self.instance.save()
        else:
            super().delete(save)


class SVGAndImageField(ImageField):
    attr_class = SVGAndImageFieldFile

    def __init__(self, *args, **kwargs):
        self.valid_extensions = ['jpg', 'jpeg', 'png', 'gif', 'svg']
        super().__init__(*args, **kwargs)

    def clean(self, value, model_instance):
        # Check for valid file extension
        file_extension = os.path.splitext(value.name)[1][1:].lower()
        if file_extension not in self.valid_extensions:
            raise ValidationError(f'Unsupported file extension: {file_extension}.')
        return super().clean(value, model_instance)
