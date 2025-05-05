
from celery import shared_task
from .models import Breakdown, Screenplay
from website import send_email

@shared_task
def process_breakdown(screenplay_id):
    
    screenplay = Screenplay.objects.get(id=screenplay_id)
    breakdown = Breakdown.objects.get(screenplay=screenplay)
    try : 
        breakdown.generate_breakdown()

        corps = """Bonjour et merci d'avoir utilisé notre service. 
Vous trouverez le dépouillement de votre film en pièce jointe.     
Il s'agit d'une première version, une base de travail que vous pourrez compléter ou éditer selon les besoins spécifiques de votre tournage.

N'hésitez pas à parler de nous dans votre entourage, et à nous envoyer :
- votre avis ou des suggestions d'améliorations par retour de mail
- des nouvelles de votre film s'il est en préparation 
- vos prochains scénarios si vous cherchez une société de production pour vous accompagner.

A bientôt !
Dorylus Productions
        """
        send_email.send(breakdown, breakdown.screenplay.user.email, corps)
    except : 
        send_email.send_error(breakdown.screenplay.user.email)

