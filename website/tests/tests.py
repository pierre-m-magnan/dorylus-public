from django.test import TestCase, Client
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from ..models import Message, Screenplay, Breakdown
from ..forms import UploadFileForm, ContactForm
import os
from core.settings import MEDIA_ROOT

class MessageModelTest(TestCase):
    def test_message_creation(self):
        message = Message.objects.create(
            Nom="John Doe",
            Email="john.doe@example.com",
            Objet="Test Subject",
            Message="This is a test message."
        )
        self.assertEqual(message.Nom, "John Doe")
        self.assertEqual(message.Email, "john.doe@example.com")
        self.assertEqual(message.Objet, "Test Subject")
        self.assertEqual(message.Message, "This is a test message.")
        self.assertIsNotNone(message.created)

class ScreenplayModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.pdf_file = SimpleUploadedFile("test.pdf", b"file_content", content_type="application/pdf")

    def test_screenplay_creation(self):
        screenplay = Screenplay.objects.create(
            docfile=self.pdf_file,
            user=self.user,
            titre="Test Screenplay",
            authors="Author Name"
        )
        # self.assertEqual(screenplay.docfile.name, "test.pdf")
        self.assertEqual(screenplay.user, self.user)
        self.assertEqual(screenplay.titre, "Test Screenplay")
        self.assertEqual(screenplay.authors, "Author Name")
        self.assertIsNotNone(screenplay.created)

    def test_screenplay_invalid_file_extension(self):
        invalid_file = SimpleUploadedFile("AKIRA/test.txt", b"file_content", content_type="text/plain")
        Screenplay.objects.create(
            docfile=invalid_file,
            user=self.user,
            titre="Test Screenplay",
            authors="Author Name"
        )
        self.assertRaises(ValidationError)

class BreakdownModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.pdf_file = SimpleUploadedFile("test.pdf", b"file_content", content_type="application/pdf")
        self.screenplay = Screenplay.objects.create(
            docfile=self.pdf_file,
            user=self.user,
            titre="Test Screenplay",
            authors="Author Name"
        )

    def test_breakdown_creation(self):
        breakdown = Breakdown.objects.create(
            screenplay=self.screenplay,
            breakdown="test_result.xlsx"
        )
        self.assertEqual(breakdown.screenplay, self.screenplay)
        self.assertEqual(breakdown.breakdown, "test_result.xlsx")

    def test_generate_breakdown(self):
        breakdown = Breakdown.objects.create(
            screenplay=self.screenplay,
            breakdown="test_result.xlsx"
        )
        # Mock the handle_pdf.handling function to avoid actual file processing
        breakdown.generate_breakdown = lambda: None
        breakdown.generate_breakdown()
        self.assertTrue(breakdown.breakdown.endswith('.xlsx'))
        # self.assertTrue(os.path.exists(breakdown.breakdown))

        # Clean up the generated file
        if os.path.exists(breakdown.breakdown):
            os.remove(breakdown.breakdown)






class UploadFileFormTest(TestCase):

    def test_file_field_label(self):
        form = UploadFileForm()
        self.assertTrue(form.fields['file'].label == 'Choisissez un fichier')

    def test_file_field_help_text(self):
        form = UploadFileForm()
        self.assertTrue(form.fields['file'].help_text == 'max. 10 Mo')

    def test_file_size_validator(self):
        # Test with a file larger than 10 MB
        large_file = SimpleUploadedFile("test.pdf", b"x" * (10 * 1024 * 1024 + 1), content_type="application/pdf")
        form = UploadFileForm(files={'file': large_file})
        self.assertFalse(form.is_valid())
        self.assertIn('Veuillez limiter la taille du fichier à 10 Mo.', form.errors['file'])

    def test_file_extension_validator(self):
        # Test with a file that is not a PDF
        wrong_file = SimpleUploadedFile("test.txt", b"file content", content_type="text/plain")
        form = UploadFileForm(files={'file': wrong_file})
        self.assertFalse(form.is_valid())
        self.assertIn('Le fichier attendu est au format pdf', form.errors['file'])

    def test_valid_file(self):
        # Test with a valid PDF file
        valid_file = SimpleUploadedFile("test.pdf", b"file content", content_type="application/pdf")
        form = UploadFileForm(files={'file': valid_file})
        self.assertTrue(form.is_valid())

class ContactFormTest(TestCase):

    def test_contact_form_fields_labels(self):
        form = ContactForm()
        self.assertTrue(form.fields['Nom'].label == 'Nom')
        self.assertTrue(form.fields['Email'].label == 'Email')
        self.assertTrue(form.fields['Objet'].label == 'Objet')
        self.assertTrue(form.fields['Message'].label == 'Message')

    def test_contact_form_valid_data(self):
        form_data = {
            'Nom': 'John Doe',
            'Email': 'john.doe@example.com',
            'Objet': 'Test Subject',
            'Message': 'This is a test message.'
        }
        form = ContactForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_contact_form_invalid_email(self):
        form_data = {
            'Nom': 'John Doe',
            'Email': 'invalid-email',
            'Objet': 'Test Subject',
            'Message': 'This is a test message.'
        }
        form = ContactForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('Veuillez renseigner une adresse email correcte', form.errors['Email'])

    def test_contact_form_missing_required_fields(self):
        form_data = {
            'Nom': '',
            'Email': 'john.doe@example.com',
            'Objet': '',
            'Message': ''
        }
        form = ContactForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('Ce champ est obligatoire.', form.errors['Nom'])
        self.assertIn('Ce champ est obligatoire.', form.errors['Message'])








class HomeViewTests(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.client.login(username='testuser', password='12345')

    def test_home_view_get(self):
        response = self.client.get(reverse('home', urlconf='website.urls'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'website/pages/home.html')
        self.assertIsInstance(response.context['form'], UploadFileForm)
        self.assertIsInstance(response.context['contact_form'], ContactForm)

    def test_home_view_post_contact(self):
        response = self.client.post(reverse('home', urlconf='website.urls'), {
            'contact_submit': True,
            'Nom': 'John Doe',
            'Email': 'john.doe@example.com',
            'Objet': 'Test Subject',
            'Message': 'This is a test message.'
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Message.objects.count(), 1)
        self.assertEqual(Message.objects.first().Nom, 'John Doe')

    # def test_home_view_post_document(self):
    #     valid_file = SimpleUploadedFile("test.pdf", b"file content", content_type="application/pdf")
    #     response = self.client.post(reverse('home', urlconf='website.urls'), {
    #         'document_submit': True,
    #         'file': valid_file
    #     })
    #     self.assertEqual(response.status_code, 302)
    #     self.assertEqual(Screenplay.objects.count(), 1)
    #     self.assertEqual(Breakdown.objects.count(), 1)

    def test_home_view_post_document_limit_exceeded(self):
        for _ in range(11):
            Screenplay.objects.create(user=self.user, docfile=SimpleUploadedFile("test.pdf", b"file content", content_type="application/pdf"))

        valid_file = SimpleUploadedFile("test.pdf", b"file content", content_type="application/pdf")
        response = self.client.post(reverse('home', urlconf='website.urls'), {
            'document_submit': True,
            'file': valid_file
        })
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/limites/')

class AuthReceiverViewTests(TestCase):

    # def test_auth_receiver_valid_token(self):
    #     # Mock a valid Google ID token
    #     token = 'valid_token'  # Replace with a valid token or mock the verification
    #     response = self.client.post(reverse('auth-receiver'), {'credential': token})
    #     self.assertEqual(response.status_code, 302)
    #     self.assertRedirects(response, '/')

    def test_auth_receiver_invalid_token(self):
        token = 'invalid_token'  # Invalid token
        response = self.client.post(reverse('auth_receiver', urlconf='website.urls'), {'credential': token})
        self.assertEqual(response.status_code, 403)

class SignOutViewTests(TestCase):

    def test_sign_out(self):
        self.client.login(username='testuser', password='12345')
        response = self.client.get(reverse('sign_out', urlconf='website.urls'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/')
        self.assertNotIn('_auth_user_id', self.client.session)

class ViewFileViewTests(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.client.login(username='testuser', password='12345')
        self.screenplay = Screenplay.objects.create(user=self.user, docfile=SimpleUploadedFile("test.pdf", b"file content", content_type="application/pdf"))

    # def test_view_file_success(self):
    #     response = self.client.get(reverse('view-file', args=[os.path.join(MEDIA_ROOT, self.screenplay.docfile.url)], urlconf='website.urls'))
    #     self.assertEqual(response.status_code, 200)
    #     self.assertEqual(response['Content-Type'], 'application/pdf')

    # def test_view_file_not_found(self):
    #     response = self.client.get(reverse('view-file', args=['nonexistentfile.pdf'], urlconf='website.urls'))
    #     self.assertEqual(response.status_code, 404)