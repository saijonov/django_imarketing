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
    vacancy = get_object_or_404(Vacancy, pk=pk)
    language = request.GET.get('lang', 'uz')
    
    if request.method == 'POST':
        form = ApplicationForm(request.POST, vacancy=vacancy, language=language)
        if form.is_valid():
            form.save()
            return render(request, 'website/vacancy_detail.html', {
                'vacancy': vacancy,
                'form': ApplicationForm(vacancy=vacancy, language=language),
                'language': language,
                'success': True
            })
    else:
        form = ApplicationForm(vacancy=vacancy, language=language)
    
    return render(request, 'website/vacancy_detail.html', {
        'vacancy': vacancy,
        'form': form,
        'language': language
    })
