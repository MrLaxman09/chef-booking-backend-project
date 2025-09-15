from .models import Chef

def chef_context(request):
    chef = None
    if request.user.is_authenticated:
        chef = Chef.objects.filter(user=request.user).first()
    return {'chef': chef}
