import io
from django.db import models
from django.core.validators import FileExtensionValidator
from website import handle_pdf
from django.dispatch import receiver
import os
from django.contrib.auth.models import User
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
import boto3
from core.settings import MEDIAFILES_LOCATION

class Message(models.Model):
    Nom = models.CharField(max_length=254)
    Email = models.EmailField()
    Objet = models.CharField(max_length=254)
    Message = models.TextField()
    created = models.DateTimeField(auto_now_add=True)

class Screenplay(models.Model):
    docfile = models.FileField(upload_to='documents/%Y/%m/%d',  validators=[FileExtensionValidator(['pdf'])])
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=1)
    created = models.DateTimeField(auto_now_add=True)
    titre = models.CharField(max_length=254, default="")
    authors = models.CharField(max_length=254, default="")
    

class Breakdown(models.Model):
    screenplay = models.OneToOneField(Screenplay, on_delete=models.CASCADE, primary_key=True)
    breakdown = models.URLField() 


    def generate_breakdown(self):
        with default_storage.open(self.screenplay.docfile.name, 'rb') as file:
            filename = self.screenplay.docfile.name
            target = filename.split('.pdf')[0] + '.xlsx'

            buffer = io.BytesIO()
            generated_file, self.screenplay.titre, self.screenplay.authors = handle_pdf.handling(file)

            generated_file.save(buffer)

            self.screenplay.save()

            self.breakdown = target
            content = ContentFile(buffer.getvalue())

            self.breakdown = default_storage.save(target, content)

            self.save()


@receiver(models.signals.post_delete, sender=Screenplay)
def auto_delete_screenplay_on_delete(sender, instance, **kwargs):
    """
    Deletes file from AWS S3 bucket
    when corresponding `Screenplay` object is deleted.
    """
    s3_client = boto3.client(
        's3',
        aws_access_key_id=os.environ['AWS_ACCESS_KEY_ID'],
        aws_secret_access_key=os.environ['AWS_SECRET_ACCESS_KEY'],
        region_name='eu-north-1'
    )
    bucket_name = os.environ['AWS_STORAGE_BUCKET_NAME']
    
    if instance.docfile:
        object_key = f"{MEDIAFILES_LOCATION}/{instance.docfile}"
        response = s3_client.delete_object(
            Bucket=bucket_name,
            Key=object_key
        )

@receiver(models.signals.post_delete, sender=Breakdown)
def auto_delete_breakdown_on_delete(sender, instance, **kwargs):
    """
    Deletes file from AWS S3 bucket
    when corresponding `Breakdown` object is deleted.
    """

    s3_client = boto3.client(
        's3',
        aws_access_key_id=os.environ['AWS_ACCESS_KEY_ID'],
        aws_secret_access_key=os.environ['AWS_SECRET_ACCESS_KEY'],
        region_name='eu-north-1'
    )
    bucket_name = os.environ['AWS_STORAGE_BUCKET_NAME']
    
    if instance.breakdown:
        object_key = f"{MEDIAFILES_LOCATION}/{instance.breakdown}"
        response = s3_client.delete_object(
            Bucket=bucket_name,
            Key=object_key
        )


@receiver(models.signals.pre_save, sender=Screenplay)
def auto_delete_file_on_change(sender, instance, **kwargs):
    """
    Deletes old file from AWS S3 bucket
    when corresponding `Screenplay` object is updated
    with new file.
    """
    if not instance.pk:
        return False
    try:
        screenplay = Screenplay.objects.get(pk=instance.pk).docfile
    except Screenplay.DoesNotExist:
        return False

    new_file = instance.docfile
    if not screenplay == new_file:
        s3_client = boto3.client(
            's3',
            aws_access_key_id=os.environ['AWS_ACCESS_KEY_ID'],
            aws_secret_access_key=os.environ['AWS_SECRET_ACCESS_KEY'],
            region_name='eu-north-1'
        )
        bucket_name = os.environ['AWS_STORAGE_BUCKET_NAME']
        object_key = f"{MEDIAFILES_LOCATION}/{screenplay}"
        response = s3_client.delete_object(
            Bucket=bucket_name,
            Key=object_key
        )