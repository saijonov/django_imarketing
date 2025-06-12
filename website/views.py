from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse
from bot.models import Vacancy
from .forms import ApplicationForm

def vacancy_list(request):
    """Display list of all published vacancies"""
    language = request.GET.get('lang', 'uz')
    vacancies = Vacancy.objects.filter(is_published=True)
    
    context = {
        'vacancies': vacancies,
        'language': language,
    }
    return render(request, 'website/vacancy_list.html', context)

def vacancy_detail(request, pk):
    """Display vacancy details and application form"""
    language = request.GET.get('lang', 'uz')
    vacancy = get_object_or_404(Vacancy, pk=pk, is_published=True)
    
    if request.method == 'POST':
        form = ApplicationForm(request.POST)
        if form.is_valid():
            application = form.save(commit=False)
            application.vacancy = vacancy
            application.save()
            return HttpResponseRedirect(reverse('vacancy_list'))
    else:
        form = ApplicationForm()
    
    context = {
        'vacancy': vacancy,
        'form': form,
        'language': language,
    }
    return render(request, 'website/vacancy_detail.html', context)
