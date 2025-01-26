from django.conf import settings


def get_admin_model(name):
    """
    Check if the given name is a custom admin.

    Args:
        name (str): The name to check.

    Returns:
        ModelAdmin: The appropriate ModelAdmin class.
    """
    if name in settings.INSTALLED_APPS:
        from unfold.admin import ModelAdmin
        return ModelAdmin

    from django.contrib.admin import ModelAdmin
    return ModelAdmin
