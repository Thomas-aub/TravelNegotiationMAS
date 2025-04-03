import os

# Dossier où se trouvent les fichiers .py (modifier si nécessaire)
dossier_source = "."  # Répertoire courant

# Fichier de sortie
fichier_sortie = "Mist.txt"

# Exclure 'extract.py'
fichier_a_exclure = "extract.py"

# Récupérer tous les fichiers Python sauf 'extract.py'
fichiers_py = [f for f in os.listdir(dossier_source) if f.endswith(".py") and f != fichier_a_exclure]

# Concaténer le contenu des fichiers dans Mist.txt
with open(fichier_sortie, "w", encoding="utf-8") as sortie:
    for fichier in fichiers_py:
        sortie.write(f"{'#' * 10} {fichier} {'#' * 10}\n\n")  # Nom du fichier encadré
        with open(os.path.join(dossier_source, fichier), "r", encoding="utf-8") as f:
            sortie.write(f.read() + "\n\n\n")  # Ajoute deux sauts de ligne après chaque fichier

print(f"Concaténation terminée ! Code sauvegardé dans {fichier_sortie}")
