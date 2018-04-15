from django.contrib import admin

# Register your models here.
from .models import Office, Person, Voter, Politician, Measure, Candidacy, Referendum, Choice, Ballot, Precinct, Poll_Worker, Election, User, Authenticator

# Register your models here.
admin.site.register(Office)
admin.site.register(Person)
admin.site.register(Voter)
admin.site.register(Politician)
admin.site.register(Measure)
admin.site.register(Candidacy)
admin.site.register(Referendum)
admin.site.register(Choice)
admin.site.register(Ballot)
admin.site.register(Precinct)
admin.site.register(Poll_Worker)
admin.site.register(Election)

admin.site.register(User)
admin.site.register(Authenticator)


'''
	admin creds
	user: root
	pw: outsourcers

'''
