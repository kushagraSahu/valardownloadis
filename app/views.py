from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, Http404, JsonResponse
from django.views.decorators.http import require_GET, require_POST, require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.core import serializers
from django.shortcuts import render, get_object_or_404, redirect
from django.core.urlresolvers import reverse

# Create your views here.

#Homepage 
def home(request):
	return render(request, 'app/home.html')

def video(request):
	return render(request, 'app/video_form.html')

@require_GET
def download_video(request):
	pass



