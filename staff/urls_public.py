from django.urls import path
from .views import StaffPublicListView, StaffPublicDetailView

urlpatterns = [
    path("staff/", StaffPublicListView.as_view()),
    path("staff/<int:pk>/", StaffPublicDetailView.as_view()),
]
