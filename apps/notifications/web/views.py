from django.shortcuts import render
from django.views.generic import TemplateView

class NotificationView(TemplateView):
    template_name = "pages/notifications_list.html"
