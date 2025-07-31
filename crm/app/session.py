def get_current_user(request):
    return request.session.get("user")
