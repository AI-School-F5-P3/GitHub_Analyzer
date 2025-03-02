# tests/test_views.py
import pytest
from django.urls import reverse
from django.test import Client
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'repo_analyzer.settings')

@pytest.fixture
def client():
    return Client()

@pytest.mark.django_db # Indica que se necesita la base de datos de Django para este test
def test_home_view(client):
    response = client.get(reverse('home'))
    assert response.status_code == 200
    assert 'home.html' in [t.name for t in response.templates]

@pytest.mark.django_db
def test_analysis_view(client):
    response = client.get(reverse('analysis'))
    assert response.status_code == 200
    assert 'analysis.html' in [t.name for t in response.templates]

@pytest.mark.django_db
def test_quick_analysis_view(client):
    response = client.get(reverse('quick_analysis'))
    assert response.status_code == 200
    assert 'quick_analysis.html' in [t.name for t in response.templates]