from django import template
from django.utils.html import mark_safe

register = template.Library()

@register.simple_tag()
def countdown_redirect(redirection_element, countdown_element, script_element=True):
    if script_element:
        script = '<script type="text/javascript">'
    else:
        script = ''
    script += """
    var remaining_seconds=$('#"""+ countdown_element +"""').text();
    function countdown() {
        if (remaining_seconds === 1) {
            window.location.replace($('#""" + redirection_element + """').attr('href'));
        } else {
            remaining_seconds--;
            $('#"""+countdown_element+"""').text(remaining_seconds);
            setTimeout(countdown, 1000);
        }
    }
    countdown();
"""
    if script_element:
        script += mark_safe('</script>')
    return mark_safe(script)