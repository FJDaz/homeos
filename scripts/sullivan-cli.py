#!/usr/bin/env python3
"""
Sullivan CLI - Interface en ligne de commande pour monitoring

Usage:
    ./scripts/sullivan-cli.py watch              # Monitoring temps réel
    ./scripts/sullivan-cli.py logs -n 50         # 50 dernières lignes
    ./scripts/sullivan-cli.py search "ERROR"     # Chercher dans les logs
    ./scripts/sullivan-cli.py stats              # Statistiques
    ./scripts/sullivan-cli.py export --today     # Export du jour
"""

import argparse
import sys
import os
import re
import subprocess
from pathlib import Path
from datetime import datetime, date
from collections import Counter
from typing import List, Optional

# Déterminer le chemin du fichier log
PROJECT_ROOT = Path(__file__).parent.parent
LOG_FILE = PROJECT_ROOT / "logs" / "sullivan_activity.log"

# Couleurs ANSI
COLORS = {
    'RED': '\033[31m',
    'GREEN': '\033[32m',
    'YELLOW': '\033[33m',
    'BLUE': '\033[34m',
    'MAGENTA': '\033[35m',
    'CYAN': '\033[36m',
    'WHITE': '\033[37m',
    'BOLD': '\033[1m',
    'RESET': '\033[0m'
}


def colorize(line: str) -> str:
    """Ajoute des couleurs à une ligne de log selon son contenu."""
    if '[ERROR]' in line:
        return f"{COLORS['RED']}{line}{COLORS['RESET']}"
    elif '[SUCCESS]' in line:
        return f"{COLORS['GREEN']}{line}{COLORS['RESET']}"
    elif '[ACTION]' in line:
        return f"{COLORS['YELLOW']}{line}{COLORS['RESET']}"
    elif '[FILE]' in line:
        return f"{COLORS['BLUE']}{line}{COLORS['RESET']}"
    elif '[KIMI]' in line:
        return f"{COLORS['CYAN']}{line}{COLORS['RESET']}"
    elif '[USER]' in line:
        return f"{COLORS['MAGENTA']}{line}{COLORS['RESET']}"
    return line


def ensure_log_exists():
    """Vérifie que le fichier log existe."""
    if not LOG_FILE.exists():
        print(f"{COLORS['RED']}❌ Fichier log non trouvé: {LOG_FILE}{COLORS['RESET']}")
        print(f"{COLORS['YELLOW']}💡 Création du fichier...{COLORS['RESET']}")
        LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
        LOG_FILE.touch()
        print(f"{COLORS['GREEN']}✅ Fichier créé{COLORS['RESET']}")


def cmd_watch(args):
    """Commande: watch - Monitoring temps réel."""
    ensure_log_exists()
    
    print(f"{COLORS['CYAN']}{COLORS['BOLD']}🔍 Sullivan Monitor — Ctrl+C pour quitter{COLORS['RESET']}")
    print(f"{COLORS['CYAN']}{'=' * 50}{COLORS['RESET']}")
    print()
    
    # Afficher les 10 dernières lignes
    print(f"{COLORS['BLUE']}📜 Dernières activités:{COLORS['RESET']}")
    try:
        with open(LOG_FILE, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            last_lines = lines[-10:] if len(lines) > 10 else lines
            for line in last_lines:
                print(colorize(line.rstrip()))
    except Exception as e:
        print(f"{COLORS['RED']}Erreur lecture: {e}{COLORS['RESET']}")
    
    print()
    print(f"{COLORS['CYAN']}👁️  Surveillance en temps réel...{COLORS['RESET']}")
    print()
    
    # Utiliser tail -f via subprocess pour le suivi temps réel
    try:
        process = subprocess.Popen(
            ['tail', '-f', str(LOG_FILE)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        for line in iter(process.stdout.readline, ''):
            if line:
                print(colorize(line.rstrip()))
                
                # Notification macOS pour les SUCCESS (optionnel)
                if sys.platform == 'darwin' and '[SUCCESS]' in line:
                    try:
                        subprocess.run([
                            'osascript', '-e',
                            f'display notification "{line[:50]}..." with title "Sullivan Monitor"'
                        ], check=False, capture_output=True)
                    except:
                        pass
                        
    except KeyboardInterrupt:
        print(f"\n{COLORS['YELLOW']}👋 Arrêt du monitor{COLORS['RESET']}")
        process.terminate()
    except FileNotFoundError:
        print(f"{COLORS['RED']}❌ Commande 'tail' non trouvée{COLORS['RESET']}")
        print(f"{COLORS['YELLOW']}💡 Utilisez: sullivan-cli.py logs -f{COLORS['RESET']}")


def cmd_logs(args):
    """Commande: logs - Afficher les dernières lignes."""
    ensure_log_exists()
    
    n = args.lines if args.lines else 20
    
    print(f"{COLORS['CYAN']}{COLORS['BOLD']}📜 Dernières {n} lignes:{COLORS['RESET']}")
    print(f"{COLORS['CYAN']}{'=' * 50}{COLORS['RESET']}")
    print()
    
    try:
        with open(LOG_FILE, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            last_lines = lines[-n:] if len(lines) > n else lines
            for line in last_lines:
                print(colorize(line.rstrip()))
    except Exception as e:
        print(f"{COLORS['RED']}❌ Erreur: {e}{COLORS['RESET']}")


def cmd_search(args):
    """Commande: search - Chercher dans les logs."""
    ensure_log_exists()
    
    pattern = args.pattern
    case_sensitive = args.case_sensitive
    today_only = args.today
    
    print(f"{COLORS['CYAN']}{COLORS['BOLD']}🔍 Recherche: '{pattern}'{COLORS['RESET']}")
    if today_only:
        print(f"{COLORS['CYAN']}📅 Aujourd'hui uniquement{COLORS['RESET']}")
    print(f"{COLORS['CYAN']}{'=' * 50}{COLORS['RESET']}")
    print()
    
    try:
        with open(LOG_FILE, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        matches = []
        today_str = date.today().strftime("%Y-%m-%d")
        
        for i, line in enumerate(lines, 1):
            # Filtrer par date si --today
            if today_only and today_str not in line:
                continue
            
            # Recherche
            if case_sensitive:
                if pattern in line:
                    matches.append((i, line))
            else:
                if pattern.lower() in line.lower():
                    matches.append((i, line))
        
        if matches:
            print(f"{COLORS['GREEN']}✅ {len(matches)} résultat(s) trouvé(s):{COLORS['RESET']}")
            print()
            for line_num, line in matches:
                # Mettre en évidence le pattern
                highlighted = highlight_pattern(line.rstrip(), pattern, case_sensitive)
                print(f"{COLORS['WHITE']}{line_num:4d}:{COLORS['RESET']} {colorize(highlighted)}")
        else:
            print(f"{COLORS['YELLOW']}⚠️  Aucun résultat pour '{pattern}'{COLORS['RESET']}")
            
    except Exception as e:
        print(f"{COLORS['RED']}❌ Erreur: {e}{COLORS['RESET']}")


def highlight_pattern(line: str, pattern: str, case_sensitive: bool) -> str:
    """Met en évidence le pattern dans la ligne."""
    if case_sensitive:
        return line.replace(pattern, f"{COLORS['BOLD']}{COLORS['YELLOW']}{pattern}{COLORS['RESET']}")
    else:
        # Remplacement insensible à la casse
        import re
        flags = 0 if case_sensitive else re.IGNORECASE
        return re.sub(f'({re.escape(pattern)})', 
                     f"{COLORS['BOLD']}{COLORS['YELLOW']}\1{COLORS['RESET']}", 
                     line, flags=flags)


def cmd_stats(args):
    """Commande: stats - Statistiques des logs."""
    ensure_log_exists()
    
    print(f"{COLORS['CYAN']}{COLORS['BOLD']}📊 Statistiques des logs{COLORS['RESET']}")
    print(f"{COLORS['CYAN']}{'=' * 50}{COLORS['RESET']}")
    print()
    
    try:
        with open(LOG_FILE, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        if not lines:
            print(f"{COLORS['YELLOW']}⚠️  Fichier log vide{COLORS['RESET']}")
            return
        
        # Compteurs
        sources = Counter()
        action_types = Counter()
        missions = []
        files_changed = []
        
        for line in lines:
            # Extraire source [KIMI], [USER], etc.
            source_match = re.search(r'\[([A-Z]+)\]', line)
            if source_match:
                sources[source_match.group(1)] += 1
            
            # Extraire type d'action [ACTION], [FILE], etc.
            action_match = re.search(r'\[([A-Z]+)\].*?\[([A-Z]+)\]', line)
            if action_match:
                action_types[action_match.group(2)] += 1
            
            # Compter missions
            if 'Mission' in line:
                missions.append(line.strip())
            
            # Compter fichiers
            if '[FILE]' in line:
                files_changed.append(line.strip())
        
        # Afficher stats
        print(f"{COLORS['BOLD']}📈 Total lignes:{COLORS['RESET']} {len(lines)}")
        print()
        
        print(f"{COLORS['BOLD']}👤 Par source:{COLORS['RESET']}")
        for source, count in sources.most_common():
            emoji = {'KIMI': '🤖', 'USER': '👤', 'TEST': '🧪', 'SYSTEM': '⚙️'}.get(source, '📝')
            print(f"  {emoji} {source}: {count}")
        print()
        
        print(f"{COLORS['BOLD']}🏷️  Par type d'action:{COLORS['RESET']}")
        for action, count in action_types.most_common():
            emoji = {'SUCCESS': '✅', 'ERROR': '❌', 'ACTION': '▶️', 
                    'FILE': '📄', 'INFO': 'ℹ️'}.get(action, '📝')
            print(f"  {emoji} {action}: {count}")
        print()
        
        print(f"{COLORS['BOLD']}🎯 Missions:{COLORS['RESET']} {len([m for m in missions if 'démarrée' in m])}")
        print(f"{COLORS['BOLD']}📁 Fichiers modifiés:{COLORS['RESET']} {len(files_changed)}")
        
        # Dernière activité
        if lines:
            last_line = lines[-1]
            timestamp_match = re.search(r'\[(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\]', last_line)
            if timestamp_match:
                print(f"\n{COLORS['BOLD']}🕐 Dernière activité:{COLORS['RESET']} {timestamp_match.group(1)}")
        
        print()
        print(f"{COLORS['GREEN']}✅ Fichier log:{COLORS['RESET']} {LOG_FILE}")
        
    except Exception as e:
        print(f"{COLORS['RED']}❌ Erreur: {e}{COLORS['RESET']}")


def cmd_export(args):
    """Commande: export - Exporter les logs."""
    ensure_log_exists()
    
    today_only = args.today
    output = args.output
    
    try:
        with open(LOG_FILE, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # Filtrer si --today
        if today_only:
            today_str = date.today().strftime("%Y-%m-%d")
            lines = [l for l in lines if today_str in l]
        
        # Déterminer la sortie
        if output:
            output_path = Path(output)
            with open(output_path, 'w', encoding='utf-8') as f:
                f.writelines(lines)
            print(f"{COLORS['GREEN']}✅ Exporté vers: {output_path}{COLORS['RESET']}")
            print(f"{COLORS['BLUE']}📄 {len(lines)} ligne(s) exportée(s){COLORS['RESET']}")
        else:
            # Sortie stdout
            print(f"{COLORS['CYAN']}{COLORS['BOLD']}📄 Logs{' (aujourd\'hui)' if today_only else ''}:{COLORS['RESET']}")
            print()
            for line in lines:
                print(line.rstrip())
    
    except Exception as e:
        print(f"{COLORS['RED']}❌ Erreur: {e}{COLORS['RESET']}")


def main():
    parser = argparse.ArgumentParser(
        prog='sullivan-cli',
        description='CLI Sullivan - Monitoring et gestion des logs',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples:
  %(prog)s watch                    # Monitoring temps réel
  %(prog)s logs -n 50               # 50 dernières lignes
  %(prog)s search "ERROR"           # Chercher les erreurs
  %(prog)s search "MISSION" --today # Missions du jour
  %(prog)s stats                    # Statistiques
  %(prog)s export --today -o rapport.txt  # Exporter le jour
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Commandes disponibles')
    
    # Commande: watch
    watch_parser = subparsers.add_parser('watch', help='Monitoring temps réel')
    
    # Commande: logs
    logs_parser = subparsers.add_parser('logs', help='Afficher les dernières lignes')
    logs_parser.add_argument('-n', '--lines', type=int, default=20,
                            help='Nombre de lignes (défaut: 20)')
    
    # Commande: search
    search_parser = subparsers.add_parser('search', help='Chercher dans les logs')
    search_parser.add_argument('pattern', help='Motif à chercher')
    search_parser.add_argument('-c', '--case-sensitive', action='store_true',
                              help='Recherche sensible à la casse')
    search_parser.add_argument('-t', '--today', action='store_true',
                              help='Limiter à aujourd\'hui')
    
    # Commande: stats
    stats_parser = subparsers.add_parser('stats', help='Statistiques des logs')
    
    # Commande: export
    export_parser = subparsers.add_parser('export', help='Exporter les logs')
    export_parser.add_argument('-t', '--today', action='store_true',
                              help='Exporter uniquement aujourd\'hui')
    export_parser.add_argument('-o', '--output', help='Fichier de sortie')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    # Exécuter la commande
    commands = {
        'watch': cmd_watch,
        'logs': cmd_logs,
        'search': cmd_search,
        'stats': cmd_stats,
        'export': cmd_export,
    }
    
    if args.command in commands:
        commands[args.command](args)
    else:
        print(f"{COLORS['RED']}❌ Commande inconnue: {args.command}{COLORS['RESET']}")
        sys.exit(1)


if __name__ == '__main__':
    main()
