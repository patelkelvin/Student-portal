from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

app_name = "student"
urlpatterns = [
    path("", views.login_view, name="login"),
    path("app", views.index, name="index"),
    path("logout", views.logout_view, name="logout"),
    path("app/<str:search>", views.templates, name="stu"),
    path("admin/<str:search>", views.templates, name="admin"),
    path("update", views.setting, name="update"),
    path("admin/<str:fileName>/upload", views.handleFileUpload, name="upload"),
    # path("csfFile", views.csvFile, name="csvFile"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
