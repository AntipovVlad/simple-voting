from .views import *
from django.urls import path

urlpatterns = [
    path('', index),
    path('index/', index),
    path('create_voting/', createVoting),
    path('voting/<int:number>', showVoting),
    path('voting_list/', votingList),
    path('login/', auth),
    path('reg/', registration),
    path('traveler/', traveler),
    path('profile/<str:login>', profile),
    path('login_exit/', exit),

]
