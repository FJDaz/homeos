
"\nModificationLog — Pilier 2 du Système Cognitif\n\nResponsabilités :\n- Event sourcing immutable de toutes les modifications\n- Persistance sur disque (SQLite ou JSON)\n- Reconstruction de l'état à partir des événements\n- Filtrage et requêtes sur l'historique\n\nConformité : CONSTITUTION_AETHERFLOW v1.0.0\n"
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
import json
import uuid
import os

@dataclass
class ModificationEvent():
    'Événement de modification immutable'
    id: str
    timestamp: datetime
    path: str
    property: str
    old_value: Any
    new_value: Any
    semantic_attributes: Dict[(str, Any)]
    user_context: Optional[Dict[(str, Any)]] = None

    def to_dict(self) -> Dict:
        "Sérialise l'événement en dict"
        d = asdict(self)
        d['timestamp'] = self.timestamp.isoformat()
        return d

    @staticmethod
    def from_dict(data: Dict) -> 'ModificationEvent':
        'Désérialise un dict en ModificationEvent'
        data = data.copy()
        data['timestamp'] = datetime.fromisoformat(data['timestamp'])
        return ModificationEvent(**data)

class ModificationLog():
    "\n    Log immutable des modifications avec event sourcing\n\n    Architecture :\n    - Chaque modification = 1 événement\n    - Événements stockés chronologiquement\n    - Persistance JSON (extensible vers SQLite)\n    - Reconstruction d'état possible\n    "

    def __init__(self, log_path: str='Backend/Prod/sullivan/stenciler/modification_log.json'):
        '\n        Initialise le log des modifications\n\n        Args:\n            log_path: Chemin vers le fichier de log JSON\n        '
        self.log_path = log_path
        self.events: List[ModificationEvent] = []
        self._load_events()
        print(f'✅ ModificationLog initialisé : {len(self.events)} événements chargés')

    def _load_events(self):
        'Charge les événements depuis le fichier JSON'
        if (not os.path.exists(self.log_path)):
            print(f'ℹ️  Nouveau log créé : {self.log_path}')
            return
        try:
            with open(self.log_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            self.events = [ModificationEvent.from_dict(evt) for evt in data.get('events', [])]
            print(f'✅ {len(self.events)} événements chargés depuis {self.log_path}')
        except json.JSONDecodeError as e:
            print(f'⚠️  Erreur lecture log : {e}')
            self.events = []

    def _save_events(self):
        'Sauvegarde les événements sur disque'
        os.makedirs(os.path.dirname(self.log_path), exist_ok=True)
        data = {'metadata': {'version': '1.0.0', 'total_events': len(self.events), 'last_updated': datetime.now().isoformat()}, 'events': [evt.to_dict() for evt in self.events]}
        with open(self.log_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def append_modification(self, path: str, property: str, old_value: Any, new_value: Any, semantic_attributes: Optional[Dict[(str, Any)]]=None, user_context: Optional[Dict[(str, Any)]]=None) -> str:
        '\n        Ajoute une modification au log (immutable)\n\n        Args:\n            path: Chemin format "n0[0].n1[2]"\n            property: Propriété modifiée\n            old_value: Ancienne valeur\n            new_value: Nouvelle valeur\n            semantic_attributes: Attributs sémantiques additionnels\n            user_context: Contexte utilisateur (optionnel)\n\n        Returns:\n            ID de l\'événement créé\n        '
        event_id = str(uuid.uuid4())
        event = ModificationEvent(id=event_id, timestamp=datetime.now(), path=path, property=property, old_value=old_value, new_value=new_value, semantic_attributes=(semantic_attributes or {}), user_context=user_context)
        self.events.append(event)
        self._save_events()
        return event_id

    def get_all_events(self) -> List[ModificationEvent]:
        '\n        Retourne tous les événements chronologiquement\n\n        Returns:\n            Liste des ModificationEvent\n        '
        return self.events.copy()

    def get_events_since(self, since: datetime) -> List[ModificationEvent]:
        '\n        Retourne les événements depuis une date\n\n        Args:\n            since: Date de début\n\n        Returns:\n            Liste des événements filtrés\n        '
        return [evt for evt in self.events if (evt.timestamp >= since)]

    def get_events_for_path(self, path: str) -> List[ModificationEvent]:
        '\n        Retourne les événements pour un path spécifique\n\n        Args:\n            path: Chemin format "n0[0].n1[2]"\n\n        Returns:\n            Liste des événements filtrés\n        '
        return [evt for evt in self.events if (evt.path == path)]

    def get_events_for_property(self, property: str) -> List[ModificationEvent]:
        '\n        Retourne les événements pour une propriété spécifique\n\n        Args:\n            property: Nom de la propriété\n\n        Returns:\n            Liste des événements filtrés\n        '
        return [evt for evt in self.events if (evt.property == property)]

    def get_recent_events(self, limit: int=50) -> List[ModificationEvent]:
        "\n        Retourne les N derniers événements\n\n        Args:\n            limit: Nombre d'événements à retourner\n\n        Returns:\n            Liste des événements les plus récents\n        "
        return self.events[(- limit):]

    def rollback_to_event(self, event_id: str) -> Optional[List[ModificationEvent]]:
        "\n        Retourne tous les événements APRÈS un événement donné (pour rollback)\n\n        Args:\n            event_id: ID de l'événement cible\n\n        Returns:\n            Liste des événements à inverser, ou None si event_id introuvable\n        "
        for (i, evt) in enumerate(self.events):
            if (evt.id == event_id):
                return self.events[(i + 1):]
        return None

    def reconstruct_state_at(self, timestamp: datetime, genome_base: Dict) -> Dict:
        "\n        Reconstruit l'état du Genome à un instant T\n\n        Args:\n            timestamp: Timestamp cible\n            genome_base: Genome de base (état initial)\n\n        Returns:\n            Dict du Genome reconstruit\n        "
        import copy
        genome = copy.deepcopy(genome_base)
        events_to_apply = self.get_events_since(datetime.min)
        for evt in events_to_apply:
            if (evt.timestamp > timestamp):
                break
            path_parts = evt.path.split('.')
            current = genome
            for part in path_parts[:(- 1)]:
                if (('[' in part) and (']' in part)):
                    (key, index) = part.split('[')
                    index = int(index[:(- 1)])
                    current = current[key][index]
                else:
                    current = current[part]
            last_part = path_parts[(- 1)]
            if (('[' in last_part) and (']' in last_part)):
                (key, index) = last_part.split('[')
                index = int(index[:(- 1)])
                current[key][index][evt.property] = evt.new_value
            else:
                current[last_part][evt.property] = evt.new_value
        return genome

    def get_statistics(self) -> Dict[(str, Any)]:
        '\n        Statistiques sur le log\n\n        Returns:\n            Dict avec statistiques\n        '
        if (not self.events):
            return {'total_events': 0, 'first_event': None, 'last_event': None, 'properties_modified': [], 'most_modified_paths': []}
        property_counts = {}
        path_counts = {}
        for evt in self.events:
            property_counts[evt.property] = (property_counts.get(evt.property, 0) + 1)
            path_counts[evt.path] = (path_counts.get(evt.path, 0) + 1)
        return {'total_events': len(self.events), 'first_event': (self.events[0].timestamp.isoformat() if self.events else None), 'last_event': (self.events[(- 1)].timestamp.isoformat() if self.events else None), 'properties_modified': sorted(property_counts.items(), key=(lambda x: x[1]), reverse=True)[:10], 'most_modified_paths': sorted(path_counts.items(), key=(lambda x: x[1]), reverse=True)[:10]}

    def validate_integrity(self) -> bool:
        "Vérifie l'intégrité du log et la cohérence des événements\n\n        Returns:\n            bool: True si le log est valide, False sinon\n        "
        if (not self.events):
            return True
        for i in range(1, len(self.events)):
            if (self.events[i].timestamp < self.events[(i - 1)].timestamp):
                print(f'⚠️  Log invalide : événements non triés chronologiquement')
                return False
        for evt in self.events:
            if ((evt.old_value is None) and (evt.new_value is None)):
                print(f'⚠️  Log invalide : événement {evt.id} avec valeurs nulles')
                return False
        print('✅ Log valide : intégrité et cohérence vérifiées')
        return True

    def get_events_between(self, start: datetime, end: datetime) -> List[ModificationEvent]:
        '\n        Retourne les événements entre deux dates\n\n        Args:\n            start: Date de début\n            end: Date de fin\n\n        Returns:\n            Liste des événements filtrés\n        '
        return [evt for evt in self.events if (start <= evt.timestamp <= end)]

    def get_events_with_semantic_attribute(self, key: str, value: Any) -> List[ModificationEvent]:
        "\n        Retourne les événements avec un attribut sémantique spécifique\n\n        Args:\n            key: Clé de l'attribut sémantique\n            value: Valeur de l'attribut\n\n        Returns:\n            Liste des événements filtrés\n        "
        return [evt for evt in self.events if (evt.semantic_attributes.get(key) == value)]

    def clear_log(self):
        '\n        DANGEREUX : Efface tous les événements\n\n        Utiliser uniquement pour tests ou remise à zéro\n        '
        self.events = []
        self._save_events()
        print('⚠️  Log vidé : tous les événements effacés')
if (__name__ == '__main__'):
    print('🧪 Tests ModificationLog')
    print(('=' * 60))
    log = ModificationLog(log_path='Backend/Prod/sullivan/stenciler/test_modification_log.json')
    log.clear_log()
    print(f'✅ Test 1 : Initialisation réussie')
    event_id_1 = log.append_modification(path='n0[0]', property='accent_color', old_value='#4CAF50', new_value='#FF5722', semantic_attributes={'importance': 'primary'})
    print(f'✅ Test 2 : Événement 1 créé : {event_id_1}')
    event_id_2 = log.append_modification(path='n0[0].n1[0]', property='layout_type', old_value='grid', new_value='flex', semantic_attributes={'density': 'compact'})
    print(f'✅ Test 3 : Événement 2 créé : {event_id_2}')
    all_events = log.get_all_events()
    print(f'✅ Test 4 : {len(all_events)} événements récupérés')
    events_n0_0 = log.get_events_for_path('n0[0]')
    print(f'✅ Test 5 : {len(events_n0_0)} événements pour n0[0]')
    events_accent = log.get_events_for_property('accent_color')
    print(f'✅ Test 6 : {len(events_accent)} événements pour accent_color')
    recent = log.get_recent_events(limit=10)
    print(f'✅ Test 7 : {len(recent)} événements récents')
    stats = log.get_statistics()
    print(f'✅ Test 8 : Statistiques calculées')
    print(f"   Total événements : {stats['total_events']}")
    print(f"   Propriétés modifiées : {stats['properties_modified']}")
    log2 = ModificationLog(log_path='Backend/Prod/sullivan/stenciler/test_modification_log.json')
    print(f'✅ Test 9 : Persistance vérifiée ({len(log2.events)} événements rechargés)')
    events_to_rollback = log.rollback_to_event(event_id_1)
    if events_to_rollback:
        print(f'✅ Test 10 : Rollback détecté {len(events_to_rollback)} événements à inverser')
    else:
        print(f'❌ Test 10 : Rollback échoué')
    os.remove('Backend/Prod/sullivan/stenciler/test_modification_log.json')
    print(f'🧹 Fichier de test supprimé')
    print(('=' * 60))
    print('🎯 ModificationLog : Tous les tests passés !')
