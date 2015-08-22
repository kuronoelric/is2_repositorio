from django.shortcuts import render
from django.http.response import HttpResponseRedirect
from django.core.urlresolvers import reverse

def principal(request):
    if request.user.is_staff:
        return HttpResponseRedirect(reverse('admin:index'))
        
    else:
        return render(request,'principal.html',{'usuario':request.user}) 


def loggedout(request):
    return render(request,'registration/logged_out.html')


def contactomail(request):
    return render(request,'registration/contactoMail.html')