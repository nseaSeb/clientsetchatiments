class Datas_test:
    @staticmethod
    def generate_test_data():
        """Génère des données de test similaires à celles qu'on obtiendrait d'un fichier"""
        # En-têtes
        headers = ["ID", "Nom", "Prénom", "Email", "Téléphone", "Ville"]
        
        # Données de test
        data = [
            [1, "Dupont", "Jean", "jean.dupont@mail.com", "0123456789", "Paris"],
            [2, "Martin", "Sophie", None, "0678912345", "Lyon"],
            [3, "Durand", "Pierre", "pierre.durand@mail.com", "", "Marseille"],
            [4, "Leroy", "Marie", "marie.leroy@mail.com", "0789456123", None],
            [5, "Moreau", "Luc", None, None, "Toulouse"]
        ]
        
        return [headers] + data

    @staticmethod
    def generate_large_test_data(rows=100):
        """Génère un grand jeu de données pour tests de performance"""
        headers = ["ID", "Nom", "Prénom", "Email", "Téléphone", "Ville"]
        data = []
        
        for i in range(1, rows+1):
            data.append([
                i,
                f"Nom_{i}",
                f"Prénom_{i}",
                f"email_{i}@test.com" if i % 3 != 0 else None,
                f"06{str(i).zfill(8)}" if i % 4 != 0 else "",
                f"Ville_{i % 10}" if i % 5 != 0 else None
            ])
        
        return [headers] + data