class Flux:
    def __init__(self, id_flux, periode, execution_time, poids):
        self.id_flux = id_flux      # ID du flux
        self.periode = periode      # Période du flux (Pi)
        self.execution_time = execution_time  # Temps d'exécution (ei)
        self.poids = poids          # Poids du flux (wi)
        self.credit = 0             # Crédit initial pour chaque flux
        self.last_execution = 0     # Temps de la dernière exécution

# Fonction d'ordonnancement Weighted Round Robin
def weighted_round_robin(flux, RL):
    temps_actuel = 0  # Temps actuel dans le round
    ordonnancement = []  # Liste de l'ordre d'exécution des flux

    # Boucle jusqu'à atteindre la longueur totale du round (RL)
    while temps_actuel < RL:
        for f in flux:
            # Ajouter le poids au crédit du flux
            f.credit += f.poids

            # Exécuter le flux tant qu'il a un crédit et qu'il reste du temps dans le round
            while f.credit >= 1 and temps_actuel < RL:
                # Si le flux est prêt à être exécuté
                if f.credit >= f.execution_time:
                    f.credit -= f.execution_time  # Décrémenter le crédit après exécution
                    temps_actuel += f.execution_time  # Incrémenter le temps actuel
                    ordonnancement.append(f.id_flux)  # Enregistrer le flux exécuté
                    f.last_execution = temps_actuel  # Mettre à jour le dernier temps d'exécution
                else:
                    # Si le crédit est insuffisant pour une exécution complète
                    break

    return ordonnancement

# Exemple d'utilisation
flux = [
    Flux(id_flux=1, periode=5, execution_time=2, poids=3),
    Flux(id_flux=2, periode=4, execution_time=1, poids=1),
    Flux(id_flux=3, periode=6, execution_time=3, poids=2),
    Flux(id_flux=3, periode=6, execution_time=3, poids=2)
]

RL = 10  # Longueur totale du round

# Exécuter l'algorithme Weighted Round Robin
resultat = weighted_round_robin(flux, RL)

print("Ordre d'exécution des flux:", resultat)