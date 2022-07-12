from django.contrib.auth.models import AnonymousUser
from django.db.models import Q
from sigi.apps.utils.models import SigiAlert
from django.template.loader import render_to_string


class SigiAlertsMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if response.streaming:
            return response
        if (
            request.method == "GET"
            and response.status_code == 200
            and "Content-Type" in response.headers
            and "html" in response.headers["Content-Type"]
            and b"</body>" in response.content
        ):
            if hasattr(request, "user"):
                user = request.user
            else:
                user = AnonymousUser()

            destinos = ["A"]
            if user.is_anonymous or not user.is_authenticated:
                destinos.append("N")
            if user.is_staff:
                destinos.append("S")
            if user.is_superuser:
                destinos.append("D")

            alertas = SigiAlert.objects.filter(
                Q(caminho=request.path_info)
                & Q(destinatarios__in=destinos)
                # & Q(Q(grupos__icontains=user.groups.all()) | Q(grupo__isnull=True))
            )

            if len(alertas) > 0:
                avisos = {}
                context = {"alertas": alertas}
                snippet = render_to_string(
                    "sigialerts/alert_snippet.html",
                    request=request,
                    context=context,
                )
                snippet += "</body>"
                response.content = response.content.replace(
                    b"</body>", snippet.encode("utf-8")
                )
        return response
