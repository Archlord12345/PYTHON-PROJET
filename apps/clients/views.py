from decimal import Decimal, ROUND_HALF_UP
from django.contrib.auth.decorators import login_required

from django.contrib import messages
from urllib.parse import urlencode

from django.core.paginator import Paginator
from django.db import IntegrityError
from django.db.models import Count, Max, Q, Sum, Value
from django.db.models.functions import Coalesce, Concat, Lower
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render

from facturation.models import Client, Facture


def _format_fcfa(amount: Decimal) -> str:
    value = (amount or Decimal("0")).quantize(Decimal("1"), rounding=ROUND_HALF_UP)
    formatted = f"{value:,}".replace(",", " ")
    return f"{formatted} FCFA"


def _split_full_name(full_name: str):
    name = (full_name or "").strip()
    if not name:
        return "", ""
    parts = name.split(maxsplit=1)
    if len(parts) == 1:
        return "", parts[0]
    return parts[0], parts[1]


def _serialize_client_row(client):
    full_name = " ".join(part for part in [client.prenom, client.nom] if part).strip() or "Client"
    last_purchase = client.last_purchase.strftime("%d/%m/%Y") if client.last_purchase else "-"
    status = "Actif" if (client.facture_count or 0) > 0 else "Inactif"
    return {
        "id": client.id,
        "name": full_name,
        "email": client.email or "",
        "phone": client.telephone or "",
        "address": client.adresse or "",
        "total_spent_raw": client.total_spent or Decimal("0"),
        "total_spent": _format_fcfa(client.total_spent or Decimal("0")),
        "last_purchase": last_purchase,
        "status": status,
        "facture_count": client.facture_count or 0,
        "client_type": client.type or "Occasionnel",
    }


@login_required
def clients_view(request):
    query = (request.GET.get("q") or "").strip()
    sort_key = (request.GET.get("sort") or "name").strip()
    direction = (request.GET.get("dir") or "asc").strip().lower()
    page_size_raw = request.GET.get("page_size") or "10"

    page_sizes = [10, 25, 50]
    try:
        page_size = int(page_size_raw)
    except ValueError:
        page_size = 10
    if page_size not in page_sizes:
        page_size = 10

    clients_qs = Client.objects.annotate(
        total_spent=Coalesce(Sum("facture__montant_TTC"), Decimal("0")),
        last_purchase=Max("facture__date_facture"),
        facture_count=Count("facture", distinct=True),
        full_name_sort=Lower(
            Concat(
                Coalesce("prenom", Value("")),
                Value(" "),
                Coalesce("nom", Value("")),
            )
        ),
    )

    if query:
        clients_qs = clients_qs.filter(
            Q(nom__icontains=query)
            | Q(prenom__icontains=query)
            | Q(email__icontains=query)
            | Q(telephone__icontains=query)
        )

    sort_map = {
        "name": ("full_name_sort",),
        "email": ("email",),
        "phone": ("telephone",),
        "total_spent": ("total_spent",),
        "last_purchase": ("last_purchase",),
        "status": ("facture_count",),
    }
    sort_fields = sort_map.get(sort_key, ("nom", "prenom"))
    order_fields = []
    for field in sort_fields:
        if direction == "desc":
            order_fields.append(f"-{field}")
        else:
            order_fields.append(field)
    clients_qs = clients_qs.order_by(*order_fields, "nom", "prenom")

    paginator = Paginator(clients_qs, page_size)
    page_obj = paginator.get_page(request.GET.get("page"))
    clients = [_serialize_client_row(client) for client in page_obj.object_list]

    total_clients = Client.objects.count()
    active_clients = Client.objects.filter(facture__isnull=False).distinct().count()
    ca_total_clients = Facture.objects.aggregate(total=Coalesce(Sum("montant_TTC"), Decimal("0")))["total"]

    def build_query(**overrides):
        params = request.GET.copy()
        for key, value in overrides.items():
            if value is None:
                params.pop(key, None)
            else:
                params[key] = str(value)
        return urlencode(params, doseq=True)

    sort_urls = {}
    for key in sort_map.keys():
        next_dir = "desc" if (sort_key == key and direction == "asc") else "asc"
        sort_urls[key] = f"?{build_query(sort=key, dir=next_dir, page=1)}"

    context = {
        "clients": clients,
        "page_obj": page_obj,
        "page_sizes": page_sizes,
        "current_page_size": page_size,
        "sort_key": sort_key,
        "direction": direction,
        "sort_urls": sort_urls,
        "query": query,
        "total_clients": total_clients,
        "active_clients": active_clients,
        "ca_total_clients": _format_fcfa(ca_total_clients or Decimal("0")),
    }
    return render(request, "clients/index.html", context)


def create_client(request):
    if request.method != "POST":
        return redirect("clients:index")

    full_name = request.POST.get("full_name", "")
    email = (request.POST.get("email") or "").strip() or None
    phone = (request.POST.get("phone") or "").strip() or None
    address = (request.POST.get("address") or "").strip() or None

    prenom, nom = _split_full_name(full_name)
    if not nom and not prenom:
        messages.error(request, "Le nom du client est requis.")
        return redirect("clients:index")

    client_type = "enregistre" if (email or phone) else "anonyme"

    try:
        Client.objects.create(
            nom=nom or None,
            prenom=prenom or None,
            email=email,
            telephone=phone,
            adresse=address,
            type=client_type,
        )
        messages.success(request, "Client créé avec succès.")
    except IntegrityError:
        messages.error(request, "Cet email est déjà utilisé par un autre client.")
    return redirect("clients:index")


def update_client(request, client_id):
    if request.method != "POST":
        return redirect("clients:index")

    client = get_object_or_404(Client, id=client_id)

    full_name = request.POST.get("full_name", "")
    email = (request.POST.get("email") or "").strip() or None
    phone = (request.POST.get("phone") or "").strip() or None
    address = (request.POST.get("address") or "").strip() or None

    prenom, nom = _split_full_name(full_name)
    if not nom and not prenom:
        messages.error(request, "Le nom du client est requis.")
        return redirect("clients:index")

    client.nom = nom or None
    client.prenom = prenom or None
    client.email = email
    client.telephone = phone
    client.adresse = address
    client.type = "enregistre" if (email or phone) else "anonyme"
    try:
        client.save(update_fields=["nom", "prenom", "email", "telephone", "adresse", "type"])
        messages.success(request, "Client mis à jour avec succès.")
    except IntegrityError:
        messages.error(request, "Cet email est déjà utilisé par un autre client.")
    return redirect("clients:index")


def client_details(request, client_id):
    client = get_object_or_404(
        Client.objects.annotate(
            total_spent=Coalesce(Sum("facture__montant_TTC"), Decimal("0")),
            last_purchase=Max("facture__date_facture"),
            facture_count=Count("facture", distinct=True),
        ),
        id=client_id,
    )

    full_name = " ".join(part for part in [client.prenom, client.nom] if part).strip() or "Client"
    history = [
        {
            "date": facture.date_facture.strftime("%d/%m/%Y"),
            "label": f"Facture #{facture.id}",
            "amount": _format_fcfa(facture.montant_TTC),
        }
        for facture in Facture.objects.filter(client=client).order_by("-date_facture")[:10]
    ]

    return JsonResponse(
        {
            "id": client.id,
            "name": full_name,
            "email": client.email,
            "phone": client.telephone,
            "address": client.adresse or "Non renseigné",
            "total_spent": _format_fcfa(client.total_spent or Decimal("0")),
            "last_purchase": client.last_purchase.strftime("%d/%m/%Y") if client.last_purchase else "-",
            "status": "Actif" if (client.facture_count or 0) > 0 else "Inactif",
            "history": history,
        }
    )


def delete_client(request, client_id):
    if request.method != "POST":
        return redirect("clients:index")

    client = get_object_or_404(Client, id=client_id)
    client.delete()
    messages.success(request, "Client supprimé avec succès.")
    return redirect("clients:index")
