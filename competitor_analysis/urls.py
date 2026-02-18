from django.urls import path
from .views import CompetitorFormView, CompetitorAnalysisFormView, CompetitorAnalysisListView
from .views import CompetitorFormView, CompetitorAnalysisMListView, CompetitorAnalysisDetailView, CompetitorCreateView, CompetitorDetailView

urlpatterns = [
    path('competitor_form/', CompetitorFormView.as_view(), name='competitor_form'),
    
    path('competitor/', CompetitorFormView.as_view(), name='competitor_list'),
    path('competitor/add/', CompetitorFormView.as_view(), name='add_competitor'),
    path('competitor/edit/<uuid:competitor_id>/', CompetitorFormView.as_view(), name='edit_competitor'),
    path('competitor/delete/<uuid:competitor_id>/', CompetitorFormView.as_view(), name='delete_competitor'),


    path('competitor_analysis_form/', CompetitorAnalysisFormView.as_view(), name='competitor_analysis_form'),
    path('competitor_analysis_list/', CompetitorAnalysisListView.as_view(), name='competitor_analysis_list'),
    # Add other paths as needed
    path('competitor_analysis/', CompetitorAnalysisMListView.as_view(), name='competitor_analysis_create'),
    path('competitor_analysis/<int:pk>/', CompetitorAnalysisDetailView.as_view(), name='competitor_analysis_detail'),
    # Add other paths as needed
    path('competitor/', CompetitorCreateView.as_view(), name='competitor_create'),
    path('competitor/<int:pk>/', CompetitorDetailView.as_view(), name='competitor_details'),



]