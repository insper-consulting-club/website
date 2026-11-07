from django.urls import path
from . import api_views

urlpatterns = [
    path('api/members/', api_views.TeamMemberListView.as_view(), name='api-members-list'),
    path('api/members/<int:pk>/', api_views.TeamMemberDetailView.as_view(), name='api-members-detail'),
    path('api/partners/', api_views.PartnerListView.as_view(), name='api-partners-list'),
    path('api/partners/<int:pk>/', api_views.PartnerDetailView.as_view(), name='api-partners-detail'),
    path('api/directorates/', api_views.DirectorateListView.as_view(), name='api-directorates-list'),
    path('api/categories/', api_views.ActivityCategoryListView.as_view(), name='api-categories-list'),
    path('api/calendar/', api_views.CalendarMonthListView.as_view(), name='api-calendar-list'),
    path('api/projects/', api_views.ProjectListView.as_view(), name='api-projects-list'),
    path('api/projects/<int:pk>/', api_views.ProjectDetailView.as_view(), name='api-projects-detail'),
    path('api/activities/', api_views.ActivityListView.as_view(), name='api-activities-list'),
    path('api/activities/<int:pk>/', api_views.ActivityDetailView.as_view(), name='api-activities-detail'),
    path('api/success-cases/', api_views.SuccessCaseListView.as_view(), name='api-success-cases-list'),
    path('api/statistics/', api_views.StatisticListView.as_view(), name='api-statistics-list'),
    path('api/news/', api_views.MediaListView.as_view(), name='api-news-list'),
    path('api/news/<str:identifier>/', api_views.MediaDetailView.as_view(), name='api-news-detail'),
    path('api/contact/', api_views.ContactCreateView.as_view(), name='api-contact'),
    path('api/selection-process/', api_views.SelectionProcessView.as_view(), name='api-selection-process'),
    path('api/health/', api_views.health, name='api-health'),
]