from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout, get_user_model
from chat.forms import LoginForm, RegisterForm,  ComposeForm 
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.conf import settings

from .models import FriendRequest, Friend, Thread, ChatMessage
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404, HttpResponseForbidden
from django.urls import reverse
from django.views.generic.edit import FormMixin

from django.views.generic import DetailView, ListView



User = get_user_model()

# Create your views here.
@login_required(login_url='/login/')
def essai_index(request):
    friend = Friend.objects.filter(current_user=request.user).first()
    friend_list = friend.users.all().exclude(id=request.user.id) if friend else []

    fr=FriendRequest.objects.filter(to_user=request.user)
    frr = FriendRequest.objects.filter(from_user=request.user)

    return render(request, 'chat/essai_index.html', {'fr':fr, 'friend':friend_list, 'frr':frr })


def login_page(request):
    form = LoginForm(request.POST or None)
    context = {
        'form': form
    }
    print(request.user.is_authenticated)
    if form.is_valid():
        print(form.cleaned_data)
        username = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('/')
        else:
            print("error.......")

    return render(request, "auth/login.html", context=context)

def register_page(request):
    form = RegisterForm(request.POST or None)
    context = {
        'form': form,
    }
    if form.is_valid():
        username = form.cleaned_data.get("username")
        email = form.cleaned_data.get("email")
        password = form.cleaned_data.get("password_first")
        new_user = User.objects.create_user(username, email, password)
    return render(request, "auth/register.html", context=context)

def logout_page(request):
    print(request)
    logout(request)
    return redirect('/')


def search_page(request):
    friend = Friend.objects.filter(current_user=request.user).first()
    friend_list = friend.users.all().exclude(id=request.user.id) if friend else []

    fr=FriendRequest.objects.filter(to_user=request.user)
    frr = FriendRequest.objects.filter(from_user=request.user)
    if request.method=='POST' :
        srch=request.POST['srh']
        if srch:
            match = User.objects.filter(Q(username__contains=srch)).exclude(id=request.user.id)
            #match = User.objects.filter(username=srch)
            if match.exists():
                print({'sr':match, 'fr':fr, 'friend':friend_list})
                return render(request,"search.html", {'sr':match, 'fr':fr, 'friend':friend_list, 'frr':frr })
            else:
                messages.error(request,'no result found')
        else:
            return redirect('/search/')
    
    return render(request,'search.html',{'fr':fr, 'friend':friend_list, 'frr':frr})


def send_friend_request(request, id):
    if request.user.is_authenticated:
        user = get_object_or_404(User, id=id)
        frequest, created = FriendRequest.objects.get_or_create(
            from_user=request.user,
            to_user=user)
        return redirect('/search/')


def cancel_friend_request(request, id):
    if request.user.is_authenticated:
        user = get_object_or_404(User, id=id)
        frequest = FriendRequest.objects.filter(
            from_user=request.user,
            to_user=user).first()
        frequest.delete()
        return redirect('/search/')


def accept_friend_request(request, id):
    #from_user = get_object_or_404(User, id=id)
    frequest = FriendRequest.objects.filter(id=id).first()
    user1 = request.user
    user2 = frequest.from_user
    friend1, created = Friend.objects.get_or_create(current_user=user1)
    friend2, created = Friend.objects.get_or_create(current_user=user2)
    #user1.profile.friends.add(user2.profile)
    #user2.profile.friends.add(user1.profile)
    friend1.users.add(user2)
    friend2.users.add(user1)

    frequest.delete()
    return redirect('/search/')


def delete_friend_request(request, id):
    #from_user = get_object_or_404(User, id=id)
    frequest = FriendRequest.objects.filter(id=id).first()
    frequest.delete()
    return redirect('/search/')


class InboxView(LoginRequiredMixin, ListView):
    template_name = 'chat/inbox.html'
    def get_queryset(self):
        return Thread.objects.by_user(self.request.user)


class ThreadView(LoginRequiredMixin, FormMixin, DetailView):
    template_name = 'chat/thread.html'
    form_class = ComposeForm
    success_url = './'

    

    def get_queryset(self):
        return Thread.objects.by_user(self.request.user)

    def get_object(self):
        other_username  = self.kwargs.get("username")
        obj, created    = Thread.objects.get_or_new(self.request.user, other_username)
        if obj == None:
            raise Http404
        return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = self.get_form()
        return context

    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return HttpResponseForbidden()
        self.object = self.get_object()
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        thread = self.get_object()
        user = self.request.user
        message = form.cleaned_data.get("message")
        ChatMessage.objects.create(user=user, thread=thread, message=message)
        return super().form_valid(form)


