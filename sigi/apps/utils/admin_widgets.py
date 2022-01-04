from django.contrib.admin.widgets import AdminFileWidget
from django.utils.safestring import mark_safe
from django.utils.translation import gettext as _


class AdminImageWidget(AdminFileWidget):

    def render(self, name, value, attrs=None):
        output = []
        if value and getattr(value, "url", None):
            image_url = value.url
            file_name = str(value)
            output.append(
                u''' <a href="%s" target="_blank"><img src="%s" width="100"
                height="100" alt="%s"/></a> <br/> %s''' %
                (image_url, image_url, file_name, _(u'Change') + ':'))
        output.append(super(AdminFileWidget, self).render(name, value, attrs))
        return mark_safe(u''.join(output))
