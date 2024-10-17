from django.http import HttpResponse
from django.shortcuts import redirect

from django.shortcuts import redirect

def unauthenticated_user(view_func):
    def wrapper_func(request, *args, **kwargs):
        if request.user.is_authenticated:
            if request.user.groups.filter(name='admin').exists():
                return redirect('adminpanel')
            elif request.user.groups.filter(name='customer').exists():
                return redirect('userpanel')
            else:
                return HttpResponse("You do not have the necessary permissions.", status=403)
        else:
            return view_func(request, *args, **kwargs)
    return wrapper_func


def allowed_users(allowed_roles=[]):
    def decorator(view_func):
        def wrapper_func(request, *args, **kwargs):
            
            if request.user.groups.exists():
                user_groups = request.user.groups.values_list('name', flat=True)
                
                if any(group in allowed_roles for group in user_groups):
                    return view_func(request, *args, **kwargs)
            return HttpResponse('Not authorized to view this page')
        return wrapper_func
    return decorator