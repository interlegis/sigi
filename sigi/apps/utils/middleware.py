from django.contrib.auth.models import AnonymousUser
from django.db.models import Q
from sigi.apps.utils.models import AlertViews, SigiAlert
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

            destinos = [SigiAlert.DESTINATARIOS_TODOS]
            if user.is_anonymous or not user.is_authenticated:
                destinos.append(SigiAlert.DESTINATARIOS_ANONIMOS)
            if user.is_staff:
                destinos.append(SigiAlert.DESTINATARIOS_EQUIPE)
            if user.is_superuser:
                destinos.append(SigiAlert.DESTINATARIOS_ADMIN)

            alertas = SigiAlert.objects.filter(
                Q(caminho=request.path_info)
                & Q(destinatarios__in=destinos)
                # & Q(Q(grupos__icontains=user.groups.all()) | Q(grupo__isnull=True))
            )

            avisos = []
            for alerta in alertas:
                if user.is_anonymous or not user.is_authenticated:
                    avisos.append([alerta, None])
                else:
                    av, created = AlertViews.objects.get_or_create(
                        alert=alerta, usuario=user
                    )
                    if av.visualizacoes < alerta.repeticao:
                        av.visualizacoes += 1
                        avisos.append(
                            [alerta, alerta.repeticao - av.visualizacoes]
                        )
                        av.save()

            if len(avisos) > 0:
                context = {"alertas": avisos}
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
