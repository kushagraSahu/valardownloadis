from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, Http404, JsonResponse
from django.views.decorators.http import require_GET, require_POST, require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.core import serializers
from django.shortcuts import render, get_object_or_404, redirect
from django.core.urlresolvers import reverse
import requests
import webbrowser
import time
import re
import dryscrape
from bs4 import BeautifulSoup
from django.core.urlresolvers import resolve

# Create your views here.
base_youtube_watch = 'https://www.youtube.com'
base_yt_url = 'https://www.youtube.com/results?search_query='
base_ss_url = 'https://www.ssyoutube.com'
global flag_stay_video
global activate_playlist
global activate_video

global hit_threshold
hit_threshold = 4

activate_video = False
activate_playlist = False



#Homepage 
def home(request):
	return render(request, 'app/home.html')

def video(request):
	return render(request, 'app/video_form.html')

def get_download_links(watch_url):
	print("Yo")
	global hit_threshold
	global flag_stay_video
	abort = False
	abort_override = False
	download_url = base_ss_url + watch_url
	session2 = dryscrape.Session()
	session2.visit(download_url)
	response=session2.body()
	soup = BeautifulSoup(response,"lxml")
	sf_result = soup.find('div', {'class':'wrapper'}).find('div', {'class':'downloader-2'}).find('div',{'id':'sf_result'})
	
	hit_count = 1
	while True:
		print(hit_count)
		print("Inside3")
		if hit_count > hit_threshold:
			abort_override = True
			break
		media_result = sf_result.find('div', {'class':'media-result'})
		if media_result != None:
			info_box = media_result.find('div', {'class': 'info-box'})
			break
		else:
			session2 = dryscrape.Session()
			session2.visit(download_url)
			response=session2.body()
			soup = BeautifulSoup(response,"lxml")
			sf_result = soup.find('div', {'class':'wrapper'}).find('div', {'class':'downloader-2'}).find('div',{'id':'sf_result'})
		hit_count += 1
	
	if not abort_override:
		dropdown_box_list = info_box.find('div', {'class': 'link-box'}).find('div', {'class': 'drop-down-box'}).find('div', {'class': 'list'}).find('div', {'class': 'links'})
		download_link_groups = dropdown_box_list.findAll('div', {'class': 'link-group'})
		
		if activate_video:
			i=0
			list_links = []
			
			for group in download_link_groups:
				download_links = group.findAll('a')
				for link in download_links:
					download = str(link['download'])
					extension = re.split(r'\.(?!\d)', download)[-1]
					class_link = link['class']
					if class_link[0] != "no-audio":
						if extension == "mp4":
							i+=1
							video_format = link['title']
							list_links.append(link)
			
			high_quality_link = list_links[0]
			to_download = high_quality_link
			to_download_url = to_download['href']
			highq_download_url = to_download_url
			if len(list_links) != 1:
				lowq_download_link = list_links[1]
				to_download = lowq_download_link
				to_download_url = to_download['href']
				lowq_download_url = to_download_url
			else:
				lowq_download_url =  highq_download_url	
			
			download_urls = {
				'high_quality_video': highq_download_url,
				'low_quality_video' : lowq_download_url
			}
			return download_urls

	else:
		return None

@require_POST
def download_video(request):
	global hit_threshold
	global activate_video
	global activate_playlist
	activate_video = True
	activate_playlist = False
	abort_override = False
	query_range = 2
	refresh_search_range = 3
	search = request.POST.get('search', '')
	if search:
		for i in range(0,refresh_search_range):
			search_url = base_yt_url + search
			session1 = dryscrape.Session()
			session1.visit(search_url)
			response=session1.body()
			soup = BeautifulSoup(response,"lxml")
			list_results = soup.find('div', {'id': 'results'}).find('ol',{'class':'section-list'}).find('ol',{'class':'item-section'}).findAll('li')
			watch_result_list = []
			i=0
			for result in list_results:
				print(i)
				if result.find('div', {'class': 'pyv-afc-ads-container'}):
					continue
				else:
					hit_count = 1
					while True:
						if hit_count > hit_threshold:
							abort_override = True
							break
						watch_result = result.find('div', {'class': "yt-lockup-content"})
						if watch_result != None:
							i+=1
							watch_result_list.append(watch_result)
							break
						hit_count += 1
						
					if(i>query_range):
						break

			#To get thumbnail photos of videos
			video_duration_list = []
			thumbnail_video_list = []
			i=0
			for result in list_results:
				if result.find('div', {'class': 'pyv-afc-ads-container'}):
					continue
				else:
					hit_count = 1
					while True:
						if hit_count > hit_threshold:
							abort_override = True
							break
						thumbnail_result = result.find('div', {'class': re.compile(r'yt-lockup-thumbnail')})
						if thumbnail_result != None:
							i+=1
							thumbnail_src = thumbnail_result.find('span', {'class': 'yt-thumb-simple'}).find('img')['src']
							thumbnail_video_list.append(thumbnail_src)
							video_time_no_text = thumbnail_result.find('span', {'class': 'video-time'})
							if video_time_no_text != None:
								video_time = video_time_no_text.text
								video_duration_list.append(video_time)
							break
						hit_count += 1
							
					if(i>query_range):
						break
			list_video_details = []
			for i in range(0,query_range+1):
				video = {}
				hit_count = 1
				while True:
					if hit_count > hit_threshold:
						break
					video_views_no_text = watch_result_list[i].find('ul', {'class': 'yt-lockup-meta-info'})
					if video_views_no_text != None:
						video_views = video_views_no_text.findAll('li')[1].text
						break
					hit_count+=1
				if hit_count > hit_threshold:
					continue
				video_views = video_views.split()[0]
				watch_url = watch_result_list[i].find('h3', {'class': 'yt-lockup-title'}).find('a')['href']
				video_title = watch_result_list[i].find('h3', {'class': 'yt-lockup-title'}).find('a').text
				video_time = video_duration_list[i]
				thumbnail_src = thumbnail_video_list[i]
				img_break = thumbnail_src.split('&')
				res1 = "w=480"
				res2 = "w=360"
				thumbnail_src = img_break[0] + "&" + res1 + "&" + res2
				for i in range(2,len(img_break)):
					thumbnail_src = thumbnail_src + "&" + img_break[i]
				download_links = get_download_links(watch_url)
				if download_links != None:
					high_quality_video_link = download_links['high_quality_video']
					low_quality_video_link = download_links['low_quality_video']
					video = {
						'title': video_title,
						'thumbnail': thumbnail_src,
						'watch_link': base_youtube_watch+watch_url,
						'views': video_views,
						'highq_link': high_quality_video_link,
						'lowq_link': low_quality_video_link,
						'time': video_time,
					}
					list_video_details.append(video)
				else:
					break

			if not list_video_details:
				continue
			context = {
				'list_videos': list_video_details,
			}
			return render(request, 'app/video_list.html', context)
			break
	else:
		url = request.POST.get('url', '')
		watch_url = "/" + url.split('/')[3]
		print(watch_url)
		while True:
			download_links = get_download_links(watch_url)
			if download_links != None:
				break
		webbrowser.open_new(download_links['high_quality_video'])
		return render(request, 'app/home.html')





