from django.shortcuts import render
from django.http.response import HttpResponse
from django.template.loader import get_template

# Create your views here.
# acesso a arquivos do fisio-admin

def fisio_admin_robots(request, js):
    template = get_template('fisio_admin/robots.txt')
    html = template.render()
    return HttpResponse(html, content_type="text/plain")

def fisio_admin_serviceworker(request, js):
    template = get_template('fisio_admin/service-worker.js')
    html = template.render()
    return HttpResponse(html, content_type="application/x-javascript")


def health_check(request):
    """
    View simples que retorna 200 OK para o Health Checker do Load Balancer.
    """
    return HttpResponse("healthy", content_type="text/plain", status=200)