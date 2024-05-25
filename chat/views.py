from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from chat.models import Chat, Profile
from datetime import datetime, timedelta


def home(request):
    return render(request, 'chat/homepage.html')


@login_required
def chat_main(request):
    try:
        Chat.objects.filter(user = request.user)[0]
    except:
        chat = Chat(user = request.user)
        chat.save()

    return redirect('chat_id', pk=1)


@login_required
def chat(request, pk):
    return render(request, 'chat/chat.html')


def profile(request, username):
    profile = get_object_or_404(Profile, user__username=username)
    return render(request, 'chat/profile.html', {'profile': profile})


class SessionTimeoutMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            last_activity = request.session.get('last_activity')
            if last_activity:
                # Check if the user's session has expired
                idle_duration = datetime.now() - last_activity
                if idle_duration > timedelta(seconds=settings.SESSION_COOKIE_AGE):
                    # Clear the session and redirect to login
                    del request.session['last_activity']
                    return redirect(reverse('login'))
            # Update last activity timestamp in the session
            request.session['last_activity'] = datetime.now()
        response = self.get_response(request)
        return response
