from .models import Chef

def chef_context(request):
    chef = None
    profile = None
    is_admin_user = False
    if request.user.is_authenticated:
        chef = Chef.objects.filter(user=request.user).first()
        profile = getattr(request.user, "profile", None)
        is_admin_user = request.user.is_superuser
    return {"chef": chef, "user_profile": profile, "is_admin_user": is_admin_user}
