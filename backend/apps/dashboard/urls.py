"""
apps/dashboard/urls.py
"""
from django.urls import path
from . import views
from django.views.generic import RedirectView

urlpatterns = [
    # Auth
    path('login/',   views.DashboardLoginView.as_view(),  name='dashboard-login'),
    path('logout/',  views.DashboardLogoutView.as_view(), name='dashboard-logout'),

    # Dashboard (requieren login — protegido con @login_required en cada view)
    path('',                           views.DashboardView.as_view(),      name='dashboard'),
    path('campaigns/new/',             views.CampaignNewView.as_view(),    name='campaign-new'),
    path('campaigns/<int:pk>/',        views.CampaignDetailView.as_view(), name='campaign-detail'),
    path('campaigns/<int:pk>/launch/', views.CampaignLaunchView.as_view(),name='campaign-launch'),
    path('campaigns/<int:pk>/status/', views.CampaignStatusView.as_view(),name='campaign-status'),
    path('campaigns/',               views.CampaignListView.as_view(),   name='campaign-list'),
    path('calls/',                   views.CallListView.as_view(),       name='call-list'),
    path('campaigns/<int:pk>/export/', views.CampaignExportView.as_view(), name='campaign-export'),
]
