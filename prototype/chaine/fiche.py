# AVERTISSEMENT : code généré avec l'aide d'une intelligence artificielle (Claude, Anthropic), non validé par
# un spécialiste de la broderie machine. Les fichiers machine (.dst) produits doivent être vérifiés par un
# professionnel qualifié avant usage : un fichier erroné peut endommager la brodeuse ou présenter un risque
# pour l'opérateur. Premier essai à vitesse réduite, sur chute de tissu.
"""Fiche couleurs (le DST ne contient aucune couleur) : ordre des fils, points et fil par bloc."""


def fiche_couleurs(nom, sequence_couleurs, qualite_fichier, profil, chemin):
    blocs = qualite_fichier["blocs"]
    l, h = qualite_fichier["dimensions_mm"]
    lignes = [f"# Fiche couleurs — {nom}", "",
              "> ⚠️ **Avertissement** : fiche et fichier machine générés automatiquement avec l'aide d'une IA, non validés "
              "par un spécialiste. Faire vérifier le fichier machine (.dst) par un professionnel qualifié avant usage : "
              "un fichier erroné peut endommager la brodeuse ou présenter un risque pour l'opérateur. Premier essai à "
              "vitesse réduite, sur chute de tissu.", "",
              f"- Dimensions : {l:.1f} × {h:.1f} mm",
              f"- Points : {qualite_fichier['points']} ; fil cousu : {qualite_fichier['fil_mm'] / 1000:.2f} m",
              f"- Changements de couleur : {qualite_fichier['changements_couleur']} ; coupes : {qualite_fichier['coupes_reelles']}",
              f"- Temps estimé : {qualite_fichier['temps_estime_min']:.1f} min (paramètres de vitesse non vérifiés)",
              f"- Profil de tissu : {profil['nom']} ; entoilage : à préciser",
              "- La machine doit être réglée sur 3 sauts consécutifs = 1 coupe.", "",
              "| Ordre | Couleur (écran) | Référence de fil | Type de bloc | Points | Fil (m) |",
              "|---|---|---|---|---|---|"]
    if len(sequence_couleurs) != len(blocs):
        lignes.insert(2, f"> **Attention** : {len(sequence_couleurs)} couleurs prévues pour {len(blocs)} blocs lus.")
    for i, b in enumerate(blocs):
        c = sequence_couleurs[i] if i < len(sequence_couleurs) else "?"
        lignes.append(f"| {i + 1} | {c} | à choisir (nuancier de l'atelier) | {b['type_deduit']} | {b['points']} | "
                      f"{b['fil_mm'] / 1000:.2f} |")
    open(chemin, "w", encoding="utf-8").write("\n".join(lignes) + "\n")
