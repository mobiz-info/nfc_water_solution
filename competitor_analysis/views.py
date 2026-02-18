from django.contrib import messages
from django.views import View
from django.shortcuts import render, redirect
from datetime import datetime

from accounts.models import Customers
from .models import CompetitorAnalysis
from product.models import Product_Default_Price_Level
from .models import CompetitorAnalysis
from datetime import date
from .forms import CompetitorForm, CompetitorAnalysisForm
from rest_framework import generics
from rest_framework.response import Response
from .models import CompetitorAnalysis
from .serializers import CompetitorAnalysisSerializer
from rest_framework import viewsets
from .models import Competitor
from .serializers import CompetitorSerializer

class CompetitorFormView(View):
    template_name = 'competitor_analysis/add_competitor.html'
    form_class = CompetitorForm

    def get(self, request):
        form = self.form_class()
        competitors = Competitor.objects.all()  # Fetch all competitors
        print("competitorscompetitors", competitors)
        return render(request, self.template_name, {'form': form, 'competitors': competitors})

    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Entry created successfully!')
            return redirect('competitor_form')
        return render(request, self.template_name, {'form': form})

class CompetitorAnalysisFormView(View):
    template_name = 'competitor_analysis/competitor_form.html'
    form_class = CompetitorAnalysisForm

    def get(self, request):
        form = self.form_class()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.created_date = date.today()
            instance.created_by = request.user
            instance.save()
            messages.success(request, 'Entry created successfully!')
            return redirect('competitor_analysis_list')
        return render(request, self.template_name, {'form': form})
    


from master.models import RouteMaster  
from django import forms
from .forms import CompetitorAnalysisFilterForm


class CompetitorAnalysisListView(View):
    template_name = 'competitor_analysis/competitor_analysis_list.html'

    def get(self, request):
        form = CompetitorAnalysisFilterForm(request.GET)
        competitor_analysis_list = CompetitorAnalysis.objects.all()

        if form.is_valid():
            route_name = form.cleaned_data.get('route_name')
            if route_name:
                # Assuming the relationship is through a ForeignKey in the Customer model
                customer_ids = Customers.objects.filter(is_guest=False, routes__route_name=route_name).values_list('customer_id', flat=True)
                # Filter using the correct field, which is 'customer_id__in'
                competitor_analysis_list = competitor_analysis_list.filter(customer_id__in=customer_ids)

        for analysis in competitor_analysis_list:
            visit_schedule = analysis.customer.visit_schedule
            current_day_of_week = datetime.now().strftime('%A')

            if visit_schedule and current_day_of_week in visit_schedule:
                current_week = visit_schedule[current_day_of_week]
                filtered_week = [week for week in current_week if week]
                number_of_visits_per_month = len(set(filtered_week))
            else:
                number_of_visits_per_month = 0

            analysis.number_of_visits_per_month = number_of_visits_per_month
            analysis.total_supply = number_of_visits_per_month * analysis.customer.no_of_bottles_required
            analysis.our_share = (analysis.total_supply / (analysis.quantity + analysis.total_supply)) * 100
            analysis.competitor_share = (analysis.quantity / (analysis.quantity + analysis.total_supply)) * 100

            try:
                our_rate = float(analysis.customer.rate)
            except (TypeError, ValueError, AttributeError):
                our_rate = 0

            analysis.price_difference = our_rate - float(analysis.price) if our_rate is not None else None

        return render(request, self.template_name, {'competitor_analysis_list': competitor_analysis_list, 'form': form})

# LIST API
class CompetitorAnalysisMListView(generics.ListCreateAPIView):
    queryset = CompetitorAnalysis.objects.all()
    serializer_class = CompetitorAnalysisSerializer

# CRUD API
class CompetitorAnalysisDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = CompetitorAnalysis.objects.all()
    serializer_class = CompetitorAnalysisSerializer

# ADD COMP API
class CompetitorCreateView(generics.ListCreateAPIView):
    queryset = Competitor.objects.all()
    serializer_class = CompetitorSerializer

# CRUD API
class CompetitorDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Competitor.objects.all()
    serializer_class = CompetitorSerializer