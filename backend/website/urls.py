from django.urls import path
from . import api_views

urlpatterns = [
    path('api/members/', api_views.MemberListView.as_view(), name='api-members-list'),
    path('api/members/<int:pk>/', api_views.MemberDetailView.as_view(), name='api-members-detail'),
    path('api/partners/', api_views.PartnerListView.as_view(), name='api-partners-list'),
    path('api/partners/<int:pk>/', api_views.PartnerDetailView.as_view(), name='api-partners-detail'),
    path('api/directorates/', api_views.DirectorateListView.as_view(), name='api-directorates-list'),
    path('api/programs/', api_views.ProgramListView.as_view(), name='api-programs-list'),
    path('api/calendar/', api_views.CalendarMonthListView.as_view(), name='api-calendar-list'),
    path('api/projects/', api_views.ProjectListView.as_view(), name='api-projects-list'),
    path('api/projects/<int:pk>/', api_views.ProjectDetailView.as_view(), name='api-projects-detail'),
    path('api/components/', api_views.ProgramComponentListView.as_view(), name='api-components-list'),
    path('api/components/<int:pk>/', api_views.ProgramComponentDetailView.as_view(), name='api-components-detail'),
    path('api/program-cases/', api_views.ProgramCaseListView.as_view(), name='api-program-cases-list'),
    path('api/statistics/', api_views.StatisticListView.as_view(), name='api-statistics-list'),
    path('api/articles/', api_views.ArticleListView.as_view(), name='api-articles-list'),
    path('api/articles/<str:identifier>/', api_views.ArticleDetailView.as_view(), name='api-articles-detail'),
    path('api/contact/', api_views.ContactCreateView.as_view(), name='api-contact'),
    path('api/selection-process/', api_views.SelectionProcessView.as_view(), name='api-selection-process'),
    path('api/health/', api_views.health, name='api-health'),
]