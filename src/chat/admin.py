from django.contrib import admin
from chat.models import Friend, FriendRequest, Thread, ChatMessage


# Register your models here.

admin.site.register(Friend)
admin.site.register(FriendRequest)

class ChatMessage(admin.TabularInline):
    model = ChatMessage

class ThreadAdmin(admin.ModelAdmin):
    inlines = [ChatMessage]
    class Meta:
        model = Thread 


admin.site.register(Thread, ThreadAdmin)
