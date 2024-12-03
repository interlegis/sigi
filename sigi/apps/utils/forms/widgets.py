from django.forms import widgets


class MonthInput(widgets.DateTimeBaseInput):
    template_name = "utils/forms/widgets/month.html"

    def __init__(self, attrs=None, format=None):
        super().__init__(attrs)
        self.format = format or "%Y-%m"
