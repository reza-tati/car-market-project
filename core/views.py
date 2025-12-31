# core/views.py (ایجاد فایل جدید)
from django.shortcuts import render

def api_docs(request):
    return render(request, 'core/api_docs.html')