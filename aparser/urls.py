from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^parse$', views.parse),
    url(r'^parse5$', views.parse5),

]
