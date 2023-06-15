def session_save(request, to_save):
    for key, value in to_save.items():
        request.session[key] = value