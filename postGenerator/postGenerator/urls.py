from django.urls import path
from post_generator.views import (
    generate_readme,
    edit_readme,
    view_readme,
    scrape_readme,
    generate_linkedin_post,
    post_on_linkedin
)

urlpatterns = [
    path("generate-readme/", generate_readme, name="generate_readme"),
    path("edit-readme/", edit_readme, name="edit_readme"),
    path("view-readme/", view_readme, name="view_readme"),
    path("scrape-readme/", scrape_readme, name="scrape_readme"),
    path("generate-linkedin-post/", generate_linkedin_post, name="generate_linkedin_post"),
    path("post-on-linkedin/", post_on_linkedin, name="post_on_linkedin"),
]
