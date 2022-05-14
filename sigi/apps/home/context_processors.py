from django.urls import reverse
from django.utils.text import slugify
from sigi.apps.home.models import Cards, Dashboard


def get_or_create_dash(usuario):
    my_dash = Dashboard.objects.filter(usuario=usuario)
    if my_dash.exists():
        return [
            {
                "slug": slugify(categoria),
                "label": categoria,
                "cards": [d.card for d in my_dash.filter(categoria=categoria)],
            }
            for categoria in sorted(
                set(my_dash.values_list("categoria", flat=True))
            )
        ]
    else:
        cards = Cards.objects.filter(default=True)
        my_dash = [
            {
                "slug": slugify(categoria),
                "label": categoria,
                "cards": [card for card in cards.filter(categoria=categoria)],
            }
            for categoria in sorted(
                set(cards.values_list("categoria", flat=True))
            )
        ]
        if not usuario.is_anonymous:
            for card in cards:
                Dashboard(
                    usuario=usuario,
                    card=card,
                    categoria=card.categoria,
                    ordem=card.ordem,
                ).save()
        return my_dash


def dashboard(request):
    if request.path != reverse("admin:index"):
        return {}
    my_dash = get_or_create_dash(request.user)
    selected = request.GET.get("dash", my_dash[0]["slug"])
    return {
        "sigi_dashes": my_dash,
        "sigi_dash_selected": selected,
        "sigi_dash_all_categories": [
            (slugify(c), c)
            for c in sorted(
                set(Cards.objects.all().values_list("categoria", flat=True))
            )
        ],
        "sigi_dash_all_cards": Cards.objects.all(),
    }
