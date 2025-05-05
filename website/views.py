from django.shortcuts import render, redirect

from django.http import HttpResponse, HttpResponseRedirect

from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.http import FileResponse, Http404
from django.core.files import File 
from google.oauth2 import id_token
from google.auth.transport import requests
from django.core.mail import send_mail
from django.utils import timezone
import os
import time
from django.contrib.auth.models import User
from django.contrib.auth import login, logout
from django.contrib.auth import get_user_model
from django.views.generic import TemplateView, FormView
from django.conf import settings
from .forms import UploadFileForm, ContactForm
from .models import Screenplay, Breakdown, Message
from website import send_email
from .tasks import process_breakdown
import sys


def breakdown_view(request):
    if request.method == "POST" and 'document_submit' in request.POST :
        form = UploadFileForm(request.POST, request.FILES)
        
        if form.is_valid():
            if not request.user.is_staff and len(Screenplay.objects.filter(user=request.user, created__month=timezone.now().month))>10:
                return HttpResponseRedirect("limites/")
            newdoc = Screenplay(docfile = request.FILES['file'], user=request.user)
            newdoc.save()
            breakdown = Breakdown(screenplay=newdoc)
            breakdown.save()
            process_breakdown.delay(newdoc.id)
            return redirect('/document-sent/') 
        else : 
            sys.stdout.write("form invalid")
    else:
        form = UploadFileForm()
        if request.session.get('has_seen_intro'):
            show_intro = False
        else : 
            request.session['has_seen_intro'] = True
            show_intro = True
    return render(
        request,
        'website/pages/home.html',
        {
            'form': form,
            'show_intro':show_intro,
        }
    )
    


class FormSuccessView(TemplateView):
    template_name = "website/pages/form-sent.html"
    
class DocumentSuccessView(TemplateView):
    template_name = "website/pages/document-sent.html"

def about_view(request):
    return render(request, "website/pages/about.html")

def productions_view(request):
    return render(request, "website/pages/productions.html")

def contact_view(request):
    if request.method == "POST":
        if 'contact_submit' in request.POST :
            contact_form = ContactForm(request.POST)
            form = UploadFileForm()
            if contact_form.is_valid():
                name = contact_form.cleaned_data['Nom']
                email = contact_form.cleaned_data['Email']
                subject = contact_form.cleaned_data['Objet']
                message = contact_form.cleaned_data['Message']

                full_message = f"""
                Received message below from {name} @ {email}, {subject}
                ________________________


                {message}
                """
                send_mail(
                    subject="Received contact form submission",
                    message=full_message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[settings.NOTIFY_EMAIL],
                )
                message = Message(Nom = name, Email = email, Objet = subject, Message=message)
                message.save()

                return redirect('/form-sent/') 

    else:


        form = UploadFileForm()
        contact_form = ContactForm()
        if request.session.get('has_seen_intro'):
            show_intro = False
        else : 
            request.session['has_seen_intro'] = True
            show_intro = True
        return render(request, "website/pages/contact.html", {
            'contact_form': contact_form,
            'show_intro':show_intro,
        })

def limites(request):
    return render(request, "website/pages/limites.html")

def erreur(request):
    return render(request, "website/pages/erreur.html")

@login_required
def view_file(request):
    try : 
        f = open(request.path, 'rb')
        myfile = File(f)
        return FileResponse(myfile, content_type="application/pdf")
    except FileNotFoundError:
        raise Http404()
    
@csrf_exempt
def auth_receiver(request):
    token = request.POST.get('credential')
    retry = 0
    while retry < 5 :
        try:
            user_data = id_token.verify_oauth2_token(
                token, requests.Request(), os.environ['GOOGLE_OAUTH_CLIENT_ID']
            )
            break
        except ValueError:
            retry += 1
            if retry == 5:
                return HttpResponse(status=403)
        time.sleep(1)
    try : 
        email = user_data['email']
        User = get_user_model()
        user, created = User.objects.get_or_create(username=email, email=email)
        login(request, user)
        request.session['user_data'] = user_data
    except : 
        return redirect("erreur/")

    return redirect('/')                        

def sign_out(request):
    if 'user_data' in request.session:
        del request.session['user_data']
    logout(request)
    return redirect('/')