import os
from django.core.mail import EmailMessage
from django.core.files.storage import default_storage
from core.settings import DEFAULT_FROM_EMAIL, MEDIAFILES_LOCATION
import boto3
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

def send(instance, address, corps):
    email = EmailMessage(
        "Votre dépouillement",
        corps,
        DEFAULT_FROM_EMAIL,
        [address],
    )
    s3_client = boto3.client(
        's3',
        aws_access_key_id=os.environ['AWS_ACCESS_KEY_ID'],
        aws_secret_access_key=os.environ['AWS_SECRET_ACCESS_KEY'],
        region_name='eu-north-1'
    )
    try :
        bucket_name = os.environ['AWS_STORAGE_BUCKET_NAME']
        object_key = f"{MEDIAFILES_LOCATION}/{instance.breakdown}"
        response = s3_client.get_object(Bucket=bucket_name, Key=object_key)
        file_content = response['Body'].read()
        email.attach(instance.breakdown, file_content, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        email.send()
    except : 
        email=EmailMessage(
            "Votre dépouillement",
            corps + "\nPS: il semble y avoir eu un problème avec l'envoi de votre dépouillement. Vous pouvez répondre à ce mail pour le signaler en incluant le fichier que vous avez reçu en pièce jointe",
            "contact@dorylus.eu",
            [address],
        )
        email.send()


def send_error(address):
    email = EmailMessage(
        "Erreur dans la génération de votre dépouillement",
        """
Bonjour et merci d'avoir utilisé notre service. 
Il semble y avoir eu un problème avec la génération de votre dépouillement, êtes-vous sûr de nous avoir envoyé le bon document ?
Si oui, cela peut être dû à une surcharge du service. Vous pouvez réessayer à un autre moment et/ou répondre à ce mail pour nous signaler un dysfonctionnement, en incluant en pièce jointe le fichier que vous avez tenté de nous envoyer.

Vous trouverez ci-joint un exemple de scénario tel que nous avons l'habitude de les recevoir.
Votre mise en page n'a pas besoin de s'y conformer rigoureusement, mais vous obtiendrez les meilleures performances si :
- votre scénario est découpé en séquences numérotées
- les entêtes de séquences sont en lettres majuscules, sur une seule ligne
- l'effet de chaque scène est décrit en des termes relativement communs : INT. JOUR / EXT.NUIT / etc.

A bientôt !
Dorylus Productions
        """,
        DEFAULT_FROM_EMAIL,
        [address],
    )
    s3_client = boto3.client(
        's3',
        aws_access_key_id=os.environ['AWS_ACCESS_KEY_ID'],
        aws_secret_access_key=os.environ['AWS_SECRET_ACCESS_KEY'],
        region_name='eu-north-1'
    )

    bucket_name = os.environ['AWS_STORAGE_BUCKET_NAME']
    object_key = f"{MEDIAFILES_LOCATION}/documents/Dorylus ipsum.pdf"
    response = s3_client.get_object(Bucket=bucket_name, Key=object_key)
    file_content = response['Body'].read()
    email.attach("Dorylus ipsum.pdf", file_content, 'application/pdf')
    email.send()
