"""
apps/dashboard/urls.py
"""
from django.urls import path
from . import views

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
]
