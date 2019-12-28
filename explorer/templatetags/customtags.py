from django import template
from django.shortcuts import reverse
register = template.Library()

@register.simple_tag(takes_context=True)
def absurl(context, view_name, *args, **kwargs):
    request = context['request']
    return request.build_absolute_uri(reverse(view_name))

@register.simple_tag(takes_context=True)
def user_or_demo(context, *args, **kwargs):
    session = context['request'].session
    if session.get('demo_mode') == True:
        return 'DEMO MODE'
    elif session.get('user_firstname', '') != '':
        return 'Hi, {}!'.format(session['user_firstname'])
    return ''
        
