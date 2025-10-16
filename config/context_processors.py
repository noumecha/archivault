from django.conf import settings

def my_setting(request):
    return {'MY_SETTING': settings}

def layout_context(request):
    return {
        "layout_path": "layout/layout_blank.html"
    }


# Add the 'ENVIRONMENT' setting to the template context
def environment(request):
    return {'ENVIRONMENT': settings.ENVIRONMENT}
