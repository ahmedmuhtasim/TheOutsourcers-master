"""outsourcers URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin
from django.urls import path
from app import views

from django.conf.urls.static import static
from django.conf import settings


urlpatterns = [
    url(r'^api/elections/(?P<pk>[0-9-]+)', views.election),
    url('api/elections/', views.elections),
    url('api/voters/', views.voters),
	url('admin/', admin.site.urls),
	url(r'^$', views.home),
	url('login/', views.login),
	url('signup/', views.signup),
	url('elections/', views.page_elections),
	url('vote/', views.vote),
	url('submitVote/', views.submit_vote),
	url(r'^results/(?P<pk>[0-9a-zA-Z-]+)', views.election_result, name='specific-results'),

	url(r'^results/', views.results, name='all-results'),
		
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

'''
admin creds
user: root
pw: outsourcers

'''
