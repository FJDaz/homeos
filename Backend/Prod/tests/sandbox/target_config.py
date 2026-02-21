# Fichier cible de test — sandbox AetherFlow
# Contenu initial minimal, à enrichir par le plan de test.

def placeholder():
    pass

# Fonction de configuration pour le système de routage intelligent
def get_config():
    """
    Retourne un dictionnaire de configuration avec des valeurs en dur.
    
    :return: dict
    """
    # config: {"env": "prod", "debug": false}  # Exemple de config
    config = {
        "host": "localhost",
        "port": 8080,
        "api_key": "aetherflow_api_key",
        "timeout": 30  # en secondes
    }
    return config

# Exemple d'utilisation
if __name__ == "__main__":
    config = get_config()
    print(config)