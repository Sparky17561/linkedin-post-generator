# In your urls.py file
from django.urls import path
from post_generator.views import linkedin_callback

urlpatterns = [
    path('', linkedin_callback),
]
