from datetime import timedelta
from decimal import Decimal, ROUND_HALF_UP
import csv
import io
import json

from django.db.models import Count, DecimalField, ExpressionWrapper, F, Sum, Value
from django.db.models.functions import Coalesce, TruncDate
from django.http import HttpResponse
from django.shortcuts import render
from django.utils import timezone
from django.utils.timesince import timesince

from facturation.models import Article, DetailFacture, Facture

try:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.platypus import SimpleDocTemplate, Spacer, Paragraph, Table, TableStyle
except Exception:  # pragma: no cover - optional dependency
    colors = None
    A4 = None
    getSampleStyleSheet = None
    SimpleDocTemplate = None
    Spacer = None
    Paragraph = None
    Table = None
    TableStyle = None


def _format_fcfa(amount: Decimal) -> str:
    value = (amount or Decimal("0")).quantize(Decimal("1"), rounding=ROUND_HALF_UP)
    formatted = f"{value:,}".replace(",", " ")
    return f"{formatted} FCFA"


def _get_period_range(period: str):
    now = timezone.now()
    if period == "day":
        start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        end = now
    elif period == "week":
        start_of_week = now - timedelta(days=now.weekday())
        start = start_of_week.replace(hour=0, minute=0, second=0, microsecond=0)
        end = now
    elif period == "month":
        start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        end = now
    elif period == "year":
        start = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
        end = now
    else:
        start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        end = now
    return start, end


def _get_previous_period_range(period: str, start, end):
    delta = end - start
    prev_end = start
    prev_start = start - delta
    return prev_start, prev_end


def report_view(request):
    period = request.GET.get("period", "day")
    start, end = _get_period_range(period)
    prev_start, prev_end = _get_previous_period_range(period, start, end)

    factures = Facture.objects.filter(date_facture__gte=start, date_facture__lte=end)
    transactions = factures.count()

    details = DetailFacture.objects.filter(facture__in=factures).select_related("article")
    produits_vendus = details.aggregate(total=Coalesce(Sum("quantite"), 0))["total"]
    ca_ttc = factures.aggregate(total=Coalesce(Sum("montant_TTC"), Decimal("0")))["total"]
    ca_ht = factures.aggregate(total=Coalesce(Sum("montant_HT"), Decimal("0")))["total"]

    panier_moyen = Decimal("0")
    if transactions:
        panier_moyen = (ca_ttc / Decimal(transactions))

    tva_collectee = factures.aggregate(total=Coalesce(Sum("montant_TVA"), Decimal("0")))["total"]

    prev_factures = Facture.objects.filter(date_facture__gte=prev_start, date_facture__lt=prev_end)
    prev_transactions = prev_factures.count()
    prev_details = DetailFacture.objects.filter(facture__in=prev_factures)
    prev_produits_vendus = prev_details.aggregate(total=Coalesce(Sum("quantite"), 0))["total"]
    prev_ca_ttc = prev_factures.aggregate(total=Coalesce(Sum("montant_TTC"), Decimal("0")))["total"]
    prev_panier_moyen = (prev_ca_ttc / Decimal(prev_transactions)) if prev_transactions else Decimal("0")

    def _trend(current: Decimal, previous: Decimal):
        if previous and previous != 0:
            diff = ((current - previous) / previous) * Decimal("100")
            diff = diff.quantize(Decimal("0.1"), rounding=ROUND_HALF_UP)
            sign = "+" if diff >= 0 else ""
            label = f"{sign}{diff}% vs période précédente"
            return label, diff >= 0
        return "N/A", None

    stock_value_expr = ExpressionWrapper(
        F("prix_TTC") * F("stock_actuel"),
        output_field=DecimalField(max_digits=12, decimal_places=2),
    )
    stock_total = Article.objects.aggregate(total=Coalesce(Sum(stock_value_expr), Decimal("0")))["total"]
    rupture = Article.objects.filter(stock_actuel=0).count()
    stock_bas = Article.objects.filter(stock_actuel__gt=0, stock_actuel__lte=F("stock_minimum")).count()
    stock_normal = Article.objects.filter(stock_actuel__gt=F("stock_minimum")).count()
    rupture_articles = list(
        Article.objects.filter(stock_actuel=0).order_by("nom").values_list("nom", flat=True)[:3]
    )

    mouvements = []
    now = timezone.now()
    for detail in details.select_related("facture").order_by("-facture__date_facture")[:2]:
        mouvements.append(
            {
                "name": detail.article.nom,
                "desc": f"-{detail.quantite} unités • Vente",
                "time": f"Il y a {timesince(detail.facture.date_facture, now)}",
            }
        )

    tva = []
    if details.exists():
        tva_rate_expr = ExpressionWrapper(
            F("article__taux_TVA"),
            output_field=DecimalField(max_digits=6, decimal_places=3),
        )
        base_expr = ExpressionWrapper(
            F("total_ligne") / (Value(1) + F("article__taux_TVA")),
            output_field=DecimalField(max_digits=12, decimal_places=2),
        )
        tva_groups = (
            details.values("article__taux_TVA")
            .annotate(base=Coalesce(Sum(base_expr), Decimal("0")), ttc=Coalesce(Sum("total_ligne"), Decimal("0")))
            .order_by("article__taux_TVA")
        )
        for row in tva_groups:
            rate = row["article__taux_TVA"] or Decimal("0")
            rate_percent = (rate * Decimal("100")).quantize(Decimal("0.1"), rounding=ROUND_HALF_UP)
            rate_label = str(rate_percent).rstrip("0").rstrip(".").replace(".", ",")
            amount = row["ttc"] - row["base"]
            tva.append(
                {
                    "rate": f"TVA {rate_label}%",
                    "base": _format_fcfa(row["base"]),
                    "amount": _format_fcfa(amount),
                }
            )

    color_hex = {
        "bg-blue-500": "#3b82f6",
        "bg-emerald-500": "#10b981",
        "bg-amber-500": "#f59e0b",
        "bg-purple-500": "#a855f7",
        "bg-slate-500": "#64748b",
        "bg-indigo-500": "#6366f1",
        "bg-slate-400": "#94a3b8",
    }
    payment_colors = {
        "carte": "bg-blue-500",
        "especes": "bg-emerald-500",
        "cheque": "bg-amber-500",
        "virement": "bg-slate-500",
        "ticket_resto": "bg-purple-500",
        "mixte": "bg-indigo-500",
    }
    paiements = []
    payments_chart = []
    payment_groups = (
        factures.values("mode_paiement")
        .annotate(total=Coalesce(Sum("montant_TTC"), Decimal("0")))
        .order_by("mode_paiement")
    )
    for row in payment_groups:
        key = row["mode_paiement"] or "mixte"
        label = dict(Facture.MODE_PAIEMENT_CHOICES).get(key, "Autre")
        total = row["total"] or Decimal("0")
        color_class = payment_colors.get(key, "bg-slate-400")
        paiements.append(
            {
                "label": label,
                "amount": _format_fcfa(total),
                "color": color_class,
            }
        )
        payments_chart.append(
            {
                "label": label,
                "value": float(total),
                "color": color_hex.get(color_class, "#94a3b8"),
            }
        )

    sales_by_day_qs = (
        factures.annotate(day=TruncDate("date_facture"))
        .values("day")
        .annotate(total=Coalesce(Sum("montant_TTC"), Decimal("0")))
        .order_by("day")
    )
    sales_by_day = [
        {"label": row["day"].strftime("%d/%m"), "value": float(row["total"] or 0)}
        for row in sales_by_day_qs
        if row["day"]
    ]

    sales_by_category_qs = (
        details.values("article__categorie")
        .annotate(total=Coalesce(Sum("total_ligne"), Decimal("0")))
        .order_by("article__categorie")
    )
    sales_by_category = [
        {"label": row["article__categorie"] or "Autres", "value": float(row["total"] or 0)}
        for row in sales_by_category_qs
    ]


    context = {
        "stats_ventes": [
            {
                "label": "CA Total",
                "value": _format_fcfa(ca_ttc),
                "trend": _trend(ca_ttc, prev_ca_ttc)[0],
                "trend_up": _trend(ca_ttc, prev_ca_ttc)[1],
            },
            {
                "label": "Transactions",
                "value": f"{transactions}",
                "trend": _trend(Decimal(transactions), Decimal(prev_transactions))[0],
                "trend_up": _trend(Decimal(transactions), Decimal(prev_transactions))[1],
            },
            {
                "label": "Panier moyen",
                "value": _format_fcfa(panier_moyen),
                "trend": _trend(panier_moyen, prev_panier_moyen)[0],
                "trend_up": _trend(panier_moyen, prev_panier_moyen)[1],
            },
            {
                "label": "Produits vendus",
                "value": f"{produits_vendus}",
                "trend": _trend(Decimal(produits_vendus), Decimal(prev_produits_vendus))[0],
                "trend_up": _trend(Decimal(produits_vendus), Decimal(prev_produits_vendus))[1],
            },
        ],
        "paiements": paiements,
        "mouvements": mouvements,
        "cartes_finances": [
            {"label": "CA HT", "value": _format_fcfa(ca_ht), "sub": "Hors taxes"},
            {"label": "TVA Collectée", "value": _format_fcfa(tva_collectee), "sub": "À reverser"},
            {"label": "CA TTC", "value": _format_fcfa(ca_ttc), "sub": "Toutes taxes comprises"},
        ],
        "tva": tva,
        "stock_total": _format_fcfa(stock_total),
        "stock_normal": stock_normal,
        "stock_bas": stock_bas,
        "rupture": rupture,
        "rupture_articles": rupture_articles,
        "period": period,
        "sales_by_day_json": json.dumps(sales_by_day),
        "sales_by_category_json": json.dumps(sales_by_category),
        "payments_chart_json": json.dumps(payments_chart),
    }
    return render(request, "report/report.html", context)


def _build_report_context(request):
    period = request.GET.get("period", "day")
    start, end = _get_period_range(period)

    factures = Facture.objects.filter(date_facture__gte=start, date_facture__lte=end)
    transactions = factures.count()

    details = DetailFacture.objects.filter(facture__in=factures).select_related("article")
    produits_vendus = details.aggregate(total=Coalesce(Sum("quantite"), 0))["total"]
    ca_ttc = factures.aggregate(total=Coalesce(Sum("montant_TTC"), Decimal("0")))["total"]
    ca_ht = factures.aggregate(total=Coalesce(Sum("montant_HT"), Decimal("0")))["total"]
    panier_moyen = (ca_ttc / Decimal(transactions)) if transactions else Decimal("0")
    tva_collectee = factures.aggregate(total=Coalesce(Sum("montant_TVA"), Decimal("0")))["total"]

    stock_value_expr = ExpressionWrapper(
        F("prix_TTC") * F("stock_actuel"),
        output_field=DecimalField(max_digits=12, decimal_places=2),
    )
    stock_total = Article.objects.aggregate(total=Coalesce(Sum(stock_value_expr), Decimal("0")))["total"]
    rupture = Article.objects.filter(stock_actuel=0).count()
    stock_bas = Article.objects.filter(stock_actuel__gt=0, stock_actuel__lte=F("stock_minimum")).count()
    stock_normal = Article.objects.filter(stock_actuel__gt=F("stock_minimum")).count()

    tva = []
    if details.exists():
        base_expr = ExpressionWrapper(
            F("total_ligne") / (Value(1) + F("article__taux_TVA")),
            output_field=DecimalField(max_digits=12, decimal_places=2),
        )
        tva_groups = (
            details.values("article__taux_TVA")
            .annotate(base=Coalesce(Sum(base_expr), Decimal("0")), ttc=Coalesce(Sum("total_ligne"), Decimal("0")))
            .order_by("article__taux_TVA")
        )
        for row in tva_groups:
            rate = row["article__taux_TVA"] or Decimal("0")
            rate_percent = (rate * Decimal("100")).quantize(Decimal("0.1"), rounding=ROUND_HALF_UP)
            rate_label = str(rate_percent).rstrip("0").rstrip(".").replace(".", ",")
            amount = row["ttc"] - row["base"]
            tva.append(
                {
                    "rate": f"TVA {rate_label}%",
                    "base": row["base"],
                    "amount": amount,
                }
            )

    paiement_groups = (
        factures.values("mode_paiement")
        .annotate(total=Coalesce(Sum("montant_TTC"), Decimal("0")))
        .order_by("mode_paiement")
    )
    paiements = []
    for row in paiement_groups:
        key = row["mode_paiement"] or "mixte"
        label = dict(Facture.MODE_PAIEMENT_CHOICES).get(key, "Autre")
        paiements.append({"label": label, "amount": row["total"]})

    return {
        "period": period,
        "start": start,
        "end": end,
        "stats": {
            "ca_ttc": ca_ttc,
            "ca_ht": ca_ht,
            "tva": tva_collectee,
            "transactions": transactions,
            "panier_moyen": panier_moyen,
            "produits_vendus": produits_vendus,
        },
        "stock": {
            "stock_total": stock_total,
            "stock_normal": stock_normal,
            "stock_bas": stock_bas,
            "rupture": rupture,
        },
        "tva_detail": tva,
        "paiements": paiements,
    }


def export_report_csv(request):
    ctx = _build_report_context(request)
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = "attachment; filename=rapport.csv"
    output = io.StringIO()
    writer = csv.writer(output)

    writer.writerow(["Rapport - Période", ctx["period"]])
    writer.writerow(["Début", ctx["start"].strftime("%Y-%m-%d %H:%M")])
    writer.writerow(["Fin", ctx["end"].strftime("%Y-%m-%d %H:%M")])
    writer.writerow([])
    writer.writerow(["--- Ventes ---"])
    writer.writerow(["CA TTC", str(ctx["stats"]["ca_ttc"])])
    writer.writerow(["CA HT", str(ctx["stats"]["ca_ht"])])
    writer.writerow(["TVA collectée", str(ctx["stats"]["tva"])])
    writer.writerow(["Transactions", str(ctx["stats"]["transactions"])])
    writer.writerow(["Panier moyen", str(ctx["stats"]["panier_moyen"])])
    writer.writerow(["Produits vendus", str(ctx["stats"]["produits_vendus"])])
    writer.writerow([])
    writer.writerow(["--- Stock ---"])
    writer.writerow(["Valeur stock", str(ctx["stock"]["stock_total"])])
    writer.writerow(["Stock normal", str(ctx["stock"]["stock_normal"])])
    writer.writerow(["Stock bas", str(ctx["stock"]["stock_bas"])])
    writer.writerow(["Rupture", str(ctx["stock"]["rupture"])])
    writer.writerow([])
    writer.writerow(["--- Finances ---"])
    writer.writerow(["CA HT", str(ctx["stats"]["ca_ht"])])
    writer.writerow(["CA TTC", str(ctx["stats"]["ca_ttc"])])
    writer.writerow(["TVA collectée", str(ctx["stats"]["tva"])])
    writer.writerow([])
    writer.writerow(["Détail TVA"])
    writer.writerow(["Taux", "Base", "Montant"])
    for row in ctx["tva_detail"]:
        writer.writerow([row["rate"], str(row["base"]), str(row["amount"])])
    writer.writerow([])
    writer.writerow(["Répartition paiements"])
    writer.writerow(["Mode", "Montant TTC"])
    for pay in ctx["paiements"]:
        writer.writerow([pay["label"], str(pay["amount"])])

    response.write(output.getvalue())
    return response


def export_report_pdf(request):
    if SimpleDocTemplate is None:
        return HttpResponse("ReportLab n'est pas installé.", status=500)

    ctx = _build_report_context(request)
    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = "attachment; filename=rapport.pdf"

    doc = SimpleDocTemplate(response, pagesize=A4)
    styles = getSampleStyleSheet()
    elements = []

    title_style = styles["Title"]
    title_style.textColor = colors.HexColor("#1f2937")
    elements.append(Paragraph("Rapport - Analyses", title_style))
    elements.append(Paragraph(f"Période : {ctx['period']}", styles["Normal"]))
    elements.append(Paragraph(f"Du {ctx['start'].strftime('%Y-%m-%d')} au {ctx['end'].strftime('%Y-%m-%d')}", styles["Normal"]))
    elements.append(Spacer(1, 12))

    stats_data = [
        ["CA TTC", _format_fcfa(ctx["stats"]["ca_ttc"])],
        ["CA HT", _format_fcfa(ctx["stats"]["ca_ht"])],
        ["TVA collectée", _format_fcfa(ctx["stats"]["tva"])],
        ["Transactions", str(ctx["stats"]["transactions"])],
        ["Panier moyen", _format_fcfa(ctx["stats"]["panier_moyen"])],
        ["Produits vendus", str(ctx["stats"]["produits_vendus"])],
    ]
    stats_table = Table(stats_data, colWidths=[200, 200])
    stats_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.whitesmoke),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.lightgrey),
                ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
                ("FONTSIZE", (0, 0), (-1, -1), 10),
                ("PADDING", (0, 0), (-1, -1), 6),
            ]
        )
    )
    elements.append(Paragraph("Synthèse - Ventes", styles["Heading2"]))
    elements.append(stats_table)
    elements.append(Spacer(1, 12))

    stock_data = [
        ["Valeur du stock", _format_fcfa(ctx["stock"]["stock_total"])],
        ["Stock normal", str(ctx["stock"]["stock_normal"])],
        ["Stock bas", str(ctx["stock"]["stock_bas"])],
        ["Rupture", str(ctx["stock"]["rupture"])],
    ]
    stock_table = Table(stock_data, colWidths=[200, 200])
    stock_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#f8fafc")),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.lightgrey),
                ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
                ("FONTSIZE", (0, 0), (-1, -1), 10),
                ("PADDING", (0, 0), (-1, -1), 6),
            ]
        )
    )
    elements.append(Paragraph("Synthèse - Stock", styles["Heading2"]))
    elements.append(stock_table)
    elements.append(Spacer(1, 12))

    finance_data = [
        ["CA HT", _format_fcfa(ctx["stats"]["ca_ht"])],
        ["TVA collectée", _format_fcfa(ctx["stats"]["tva"])],
        ["CA TTC", _format_fcfa(ctx["stats"]["ca_ttc"])],
    ]
    finance_table = Table(finance_data, colWidths=[200, 200])
    finance_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#f8fafc")),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.lightgrey),
                ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
                ("FONTSIZE", (0, 0), (-1, -1), 10),
                ("PADDING", (0, 0), (-1, -1), 6),
            ]
        )
    )
    elements.append(Paragraph("Synthèse - Finances", styles["Heading2"]))
    elements.append(finance_table)
    elements.append(Spacer(1, 12))

    tva_data = [["Taux", "Base", "Montant"]]
    for row in ctx["tva_detail"]:
        tva_data.append([row["rate"], _format_fcfa(row["base"]), _format_fcfa(row["amount"])])
    if len(tva_data) == 1:
        tva_data.append(["N/A", "-", "-"])
    tva_table = Table(tva_data, colWidths=[120, 140, 140])
    tva_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#f1f5f9")),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.lightgrey),
                ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
                ("FONTSIZE", (0, 0), (-1, -1), 10),
                ("PADDING", (0, 0), (-1, -1), 6),
            ]
        )
    )
    elements.append(Paragraph("Détail TVA", styles["Heading2"]))
    elements.append(tva_table)
    elements.append(Spacer(1, 12))

    pay_data = [["Mode de paiement", "Montant TTC"]]
    for pay in ctx["paiements"]:
        pay_data.append([pay["label"], _format_fcfa(pay["amount"])])
    pay_table = Table(pay_data, colWidths=[250, 150])
    pay_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#f1f5f9")),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.lightgrey),
                ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
                ("FONTSIZE", (0, 0), (-1, -1), 10),
                ("PADDING", (0, 0), (-1, -1), 6),
            ]
        )
    )
    elements.append(Paragraph("Paiements", styles["Heading2"]))
    elements.append(pay_table)

    doc.build(elements)
    return response
