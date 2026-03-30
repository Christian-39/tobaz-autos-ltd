def theme_context(request):
    """
    Context processor to add theme preference to all templates.
    """
    theme = request.COOKIES.get('theme', 'light')
    return {
        'theme': theme,
        'is_dark_mode': theme == 'dark',
    }
