from django.conf import settings
from django.db import models
from django.core.files.base import ContentFile
from PIL import Image
from django.core.files import File
from io import BytesIO


class CreationModificationDateAbstractModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    modified_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    is_deleted = models.BooleanField(default=False, null=True, blank=True)

    class Meta:
        abstract = True


class UploadFile(CreationModificationDateAbstractModel):
    file = models.FileField(null=True, blank=True)
    thumbnail_file = models.ImageField(null=True, blank=True)
    file_tags = models.CharField(max_length=128, null=True, blank=True)
    file_url = models.CharField(max_length=128, null=True, blank=True)
    file_name = models.CharField(max_length=128, null=True, blank=True)
    bucket_name = models.CharField(max_length=128, default="hamresan-bucket")

    def __str__(self):
        return self.file.url

    def save(self, *args, **kwargs):
        file_extension = self.file.name.split('.')[-1].lower()

        if file_extension == 'svg':
            self.thumbnail_file = self.file  # Assign the original SVG file as thumbnail
        else:
            thumb_io = BytesIO()
            process_and_upload_image(self.file, thumb_io)

            thumb_io.seek(0)  # Reset the BytesIO object's pointer
            thumb_file_name = f"{self.file.name.rsplit('.', 1)[0]}_thumbnail.jpg"
            self.thumbnail_file.save(thumb_file_name, ContentFile(thumb_io.read()), save=False)

        super().save(*args, **kwargs)


def process_and_upload_image(image, thumb_io):
    # Open the image and compress it
    with Image.open(image) as img:
        img = img.convert("RGB")
        img.thumbnail((800, 800))  # Resize the image, preserving aspect ratio
        img.save(thumb_io, format="JPEG", quality=70)  #
