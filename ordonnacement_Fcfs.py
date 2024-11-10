class OrdonnancementFCFS:
    def __init__(self):
        """Initialise une file d'attente vide pour les demandes."""
        self.file_d_attente = []

    def ajouter_demande(self, source, destination, bande_passante_minimale):
        """Ajoute une demande de chemin dans la file d'attente."""
        self.file_d_attente.append((source, destination, bande_passante_minimale))
        print(f"Demande ajoutée : Source {source}, Destination {destination}, Bande passante minimale {bande_passante_minimale}")

    def traiter_demandes(self, dijkstra_instance):
        """Traite toutes les demandes dans la file d'attente dans l'ordre FCFS."""
        while self.file_d_attente:
            source, destination, bande_passante_minimale = self.file_d_attente.pop(0)
            print(f"Traitement de la demande : Source {source}, Destination {destination}, Bande passante minimale {bande_passante_minimale}")
            chemin = dijkstra_instance.search_path(source, destination, bande_passante_minimale)
            if chemin:
                visualisation = input("Voulez-vous visualiser le chemin sur le graphe? (O/N): ").strip().lower()
                if visualisation == 'o':
                    dijkstra_instance.visualiser_graphe(chemin)
