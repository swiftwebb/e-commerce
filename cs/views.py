from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Chat, ChatMessage
from .forms import ChatMessageForm
from django.contrib.auth.models import User
from django.http import HttpResponse


@login_required
def start_chat(request):
    if request.user.is_staff:
        return HttpResponse("Staff cannot initiate chats.", status=403)

    existing_chat = Chat.objects.filter(customer=request.user).first()
    if existing_chat:
        return redirect('cs:chat_detail', chat_id=existing_chat.id)

    staff = User.objects.filter(is_staff=True).first()
    if not staff:
        return HttpResponse("No staff available", status=503)

    try:
        chat = Chat.objects.create(customer=request.user, staff=staff)
        return redirect('cs:chat_detail', chat_id=chat.id)
    except Exception as e:
        return HttpResponse(f"Failed to create chat: {e}", status=500)


@login_required
def chat_detail(request, chat_id):
    chat = get_object_or_404(Chat, id=chat_id)

    if request.user != chat.customer and request.user != chat.staff:
        return redirect('core:index')

    if request.method == 'POST':
        form = ChatMessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.chat = chat
            message.sender = request.user
            message.save()
            return redirect('cs:chat_detail', chat_id=chat.id)
    else:
        form = ChatMessageForm()

    return render(request, 'chat_detail.html', {
        'chat': chat,
        'messagesf': chat.messagesf.order_by('timestamp'),
        'form': form,
    })


@login_required
def chat_list(request):
    try:
        if request.user.is_staff:
            chats = Chat.objects.all()
        else:
            chats = Chat.objects.filter(customer=request.user)
        
        return render(request, 'chat_list.html', {
            'chats': chats
        })
    except Exception as e:
        return HttpResponse(f"Error: {e}", status=500)
