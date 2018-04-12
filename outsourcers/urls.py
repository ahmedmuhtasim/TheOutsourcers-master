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
from django.conf.urls.static import static
from django.conf import settings
from app import views

#router.register("voters", VoterViewSet)
#router.register("ballots", BallotViewSet)
request_override_map = {
    'get': 'get',
    'post': 'post',
    'put': 'put',
    'delete': 'delete'
}
voter_endpoint = views.VoterViewSet.as_view(request_override_map)
election_endpoint = views.ElectionViewSet.as_view(request_override_map)
ballot_endpoint = views.BallotViewSet.as_view(request_override_map)
person_endpoint = views.PersonViewSet.as_view(request_override_map)
precinct_endpoint = views.PrecinctViewSet.as_view(request_override_map)
measure_endpoint = views.MeasureViewSet.as_view(request_override_map)
politician_endpoint = views.PoliticianViewSet.as_view(request_override_map)
office_endpoint = views.OfficeViewSet.as_view(request_override_map)
referendum_endpoint = views.ReferendumViewSet.as_view(request_override_map)
candidacy_endpoint = views.CandidacyViewSet.as_view(request_override_map)

urlpatterns = [
    # Internal API Endpoints
    url(r'^api/voters/(?P<pk>[0-9-]+)', voter_endpoint, name='voter-detail'),
    url(r'^api/voters/', voter_endpoint, name='voter-list'),
    url(r'^api/elections/(?P<pk>[0-9-]+)', election_endpoint, name='election-detail'),
    url(r'^api/elections/', election_endpoint, name='election-list'),
    url(r'^api/ballots/(?P<pk>[0-9-]+)', ballot_endpoint, name='ballot-detail'),
    url(r'^api/ballots/', ballot_endpoint, name='ballot-list'),
    url(r'^api/persons/(?P<pk>[0-9-]+)', person_endpoint, name='person-detail'),
    url(r'^api/persons/', person_endpoint, name='person-list'),
    url(r'^api/precincts/(?P<pk>[0-9-]+)', precinct_endpoint, name='precinct-detail'),
    url(r'^api/precincts/', precinct_endpoint, name='precinct-list'),
    url(r'^api/measures/(?P<pk>[0-9-]+)', measure_endpoint, name='measure-detail'),
    url(r'^api/measures/', measure_endpoint, name='measure-list'),
    url(r'^api/politicians/(?P<pk>[0-9-]+)', politician_endpoint, name='politician-detail'),
    url(r'^api/politicians/', politician_endpoint, name='politician-list'),
    url(r'^api/offices/(?P<pk>[0-9-]+)', office_endpoint, name='office-detail'),
    url(r'^api/offices/', office_endpoint, name='office-list'),
    url(r'^api/referendums/(?P<pk>[0-9-]+)', referendum_endpoint, name='referendum-detail'),
    url(r'^api/referendums/', referendum_endpoint, name='referendum-list'),
    url(r'^api/candidacies/(?P<pk>[0-9-]+)',candidacy_endpoint, name='candidacy-detail'),
    url(r'^api/candidacies/', candidacy_endpoint, name='candidacy-list'),


	url('admin/', admin.site.urls),
	url(r'^$', views.home, name='home'),
	url('login/', views.login),
    url('signupConfirmation/', views.signup_confirmation, name='signup_confirmation'),
	url('signup/', views.signup),
	url('signout/', views.signout),
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
