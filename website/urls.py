from django.urls import path, re_path


from .views import (
    breakdown_view,
    about_view,
    productions_view,
    contact_view,
    view_file,
    limites,
    auth_receiver,
    sign_out,
    erreur,
    FormSuccessView,
    DocumentSuccessView,
)

app_name = "website"

urlpatterns = [
    path("about/", about_view, name="about"),
    path("productions/", productions_view, name="productions"),
    path("", breakdown_view, name="breakdown"),
    path("contact/", contact_view, name="contact"),
    path('limites/', limites, name='limites'),
    re_path(r'media/documents/[0-9]{4}/[0-9]{2}/[0-9]{2}/.+', view_file, name="view-file"),
    path('sign-out/', sign_out, name='sign_out'),
    path('auth-receiver/', auth_receiver, name='auth_receiver'),
    path('erreur/', erreur, name='erreur'),
    path("form-sent/", FormSuccessView.as_view(), name="form-sent"),
    path('document-sent/', DocumentSuccessView.as_view(), name='document-success'),
]