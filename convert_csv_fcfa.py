#!/usr/bin/env python3
"""
Script de conversion EUR → FCFA pour le fichier CSV d'articles
Taux de conversion : 1 EUR = 655.957 FCFA (taux fixe CEMAC)
"""

import csv
import sys

TAUX_CONVERSION = 655.957  # 1 EUR = 655.957 FCFA

def convertir_eur_vers_fcfa(valeur_euro):
    """Convertit une valeur en EUR vers FCFA"""
    try:
        return round(float(valeur_euro) * TAUX_CONVERSION, 2)
    except (ValueError, TypeError):
        return valeur_euro

def convertir_csv(fichier_entree, fichier_sortie):
    """Convertit le fichier CSV EUR vers FCFA"""

    with open(fichier_entree, 'r', encoding='utf-8') as f_in, \
         open(fichier_sortie, 'w', encoding='utf-8', newline='') as f_out:

        reader = csv.DictReader(f_in)
        fieldnames = reader.fieldnames

        writer = csv.DictWriter(f_out, fieldnames=fieldnames)
        writer.writeheader()

        lignes_converties = 0
        for row in reader:
            # Convertir Prix HT
            if row.get('Prix HT'):
                row['Prix HT'] = convertir_eur_vers_fcfa(row['Prix HT'])

            # Convertir Prix TTC
            if row.get('Prix TTC'):
                row['Prix TTC'] = convertir_eur_vers_fcfa(row['Prix TTC'])

            writer.writerow(row)
            lignes_converties += 1

    return lignes_converties

if __name__ == '__main__':
    fichier_entree = '/home/ravel/Documents/CODES/PYTHON-PROJET/articles_import.csv'
    fichier_sortie = '/home/ravel/Documents/CODES/PYTHON-PROJET/articles_import_fcfa.csv'

    print(f"🔄 Conversion EUR → FCFA (taux: {TAUX_CONVERSION})")
    print(f"📁 Fichier source : {fichier_entree}")

    lignes = convertir_csv(fichier_entree, fichier_sortie)

    print(f"✅ {lignes} lignes converties avec succès")
    print(f"💾 Fichier de sortie : {fichier_sortie}")
    print(f"\n📊 Exemple de conversion :")
    print(f"   150.00 EUR → {convertir_eur_vers_fcfa(150.00):,.2f} FCFA")
    print(f"   3.59 EUR → {convertir_eur_vers_fcfa(3.59):,.2f} FCFA")
