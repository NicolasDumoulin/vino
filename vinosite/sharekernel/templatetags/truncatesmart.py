# -*- coding: utf8 -*-
from django.utils.html import mark_safe
from django import template
register = template.Library()
from django.template import Template, Context

@register.simple_tag
def truncatesmartjavascript():
    """
    Returns the javascript code for collapsing/expanding the truncated texts.
    """
    return mark_safe("""<script type="text/javascript">
    $( document ).ready(function() {
        $('.truncated').hide();                 // Hide the text initially
        $('.show-truncated').on('click', function(){
            $(this).toggleClass('glyphicon-plus glyphicon-minus')   // Swap the icon
                .prev().toggle();                    // Hide/show the text
        });
    });
</script>
""")

@register.filter
def truncatesmart(value, limit):
    """
    Truncates a string after a given number of chars keeping whole words.
    
    Usage:
        {{ string|truncatesmart }}
        {{ string|truncatesmart:50 }}
    """
    try:
        limit = int(limit)
    # invalid literal for int()
    except ValueError:
        # Fail silently.
        return value    
    # Make sure it's unicode
    value = unicode(value)
    # Return the string itself if length is smaller or equal to the limit
    if len(value) <= limit:
        return value
    # Cut the string
    begin = value[:limit]
    end = value[limit:]
    # last space of begin will be lost if any by following split
    if begin[-1]==' ':
        end=' '+end
    # Break into words and give the last one (may be truncated) to the end part
    begin = begin.split(' ')
    end = begin[-1]+end
    # remove the last word (maybe truncated) and collate again
    begin = ' '.join(begin[:-1])
    return Template(begin + u'… <span class="truncated">' + end + '</span><span class="show-truncated glyphicon glyphicon-plus" aria-hidden="true"></span>').render(Context())
