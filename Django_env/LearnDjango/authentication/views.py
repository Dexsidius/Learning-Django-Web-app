from django.shortcuts import redirect, render
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.core.mail import send_mail, EmailMessage
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str

from . tokens import generate_token
from LearnDjango import settings

# Create your views here.
def home(request):
    return render(request, "authentication/index.html")

def signup(request):

    if request.method == "POST":
        username = request.POST['username']
        email = request.POST['email']
        passwrd = request.POST['pass1']
        vpasswrd = request.POST['pass2']
        fname = request.POST['fname']
        lname = request.POST['lname']

        if User.objects.filter(username=username):
            messages.error(request, "Username already exists! Please try another username.")
            return redirect('home')

        if User.objects.filter(email=email):
            messages.error(request, "Email is already associated with anther account")
            return redirect('home')

        if (len(passwrd) < 8):
            messages.error(request, "Password must be at least 8 characters/numbers")
        
        if (passwrd != vpasswrd):
            messages.error(request, "Password does not match")

        myuser = User.objects.create_user(username, email, passwrd)
        myuser.first_name = fname
        myuser.last_name = lname
        myuser.active = False
        
        myuser.save()

        messages.success(request, "Your Account has been created")

        # Welcome Email after signup

        subject = "Welcome to Django learning area w/ Dexsidius"
        message = "Hello " + myuser.first_name + " this is Dexsidius messaging you from the Django learning site.  You are welcome to do with this email as you want but just don't be a turd."
        from_email = settings.EMAIL_HOST_USER
        to_email = [myuser.email]
        send_mail(subject, message, from_email, to_email, fail_silently = True)

        #Email Address for Confirmation Email

        current_size = get_current_site(request)
        email_subject = "Confirm your email @ LearnDjango - Dexsidius"
        message2 = render_to_string('email_confirmation.html'), {
            'name': myuser.first_name,
            'domain': get_current_site.domain,
            'uid': urlsafe_base64_encode(force_bytes(myuser.pk)),
            'token': generate_token.make_token(myuser)

        }
        email = EmailMessage(
            email_subject, 
            message2,
            settings.EMAIL_HOST_USER,
            [myuser.email]
        )
        email.fail_silently = True
        email.send() 

        return redirect('signin')


    return render(request, "authentication/signup.html")

def signin(request):

    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['pass1']

        user = authenticate(username=username, password=password)

        if user is not None:
            login(request, user)
            fname = user.first_name
            return render(request, 'authentication/index.html', {'fname': fname})

        else:
            messages.error(request, "Bad Login!  Please try again")
            return redirect('home')
            


    return render(request, "authentication/signin.html")

def signout(request):
    logout(request)
    messages.success(request, "Goodbye")
    return redirect('home')

def activate(request, uidb64, token):

    try: 
        uid = force_str(urlsafe_base64_decode(uidb64))
        myuser = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        myuser = None
    
    if myuser is not None and generate_token.check_token(myuser, token):
        myuser.active = True

    

