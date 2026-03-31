#!/usr/bin/env python3
"""
MiMo CLI — Interactive chat with Xiaomi MiMo AI.
"""
import asyncio
import sys
import os
from pathlib import Path

# Fix path to allow importing Backend
project_root = Path(__file__).resolve().parents[3]
sys.path.append(str(project_root))

try:
    from Backend.Prod.models.mimo_client import MimoClient
    from Backend.Prod.core.cost_tracker import record_cost, get_cost_tracker
    from Backend.Prod.scripts.mimo_monitor import show_mimo_status
except ImportError as e:
    print(f"❌ Critical Error: Could not load AetherFlow Backend modules. {e}")
    sys.exit(1)

async def chat():
    client = MimoClient()
    
    # Check if API KEY is present
    if not client.api_key:
        print("❌ Error: MIMO_KEY is not configured in your .env file.")
        await client.close()
        return

    print("="*60)
    print("🚀 XIAOMI MIMO - INTERFACE CLI (AetherFlow)")
    print("Tapez 'exit' pour quitter, '/status' pour l'usage, '/clear' pour reset.")
    print("="*60)
    
    context_history = []
    
    while True:
        try:
            user_input = input("\n👤 Vous > ").strip()
            if not user_input: continue
            
            if user_input.lower() in ('exit', 'quit', 'q'): 
                break
                
            if user_input.lower() == '/status':
                show_mimo_status()
                continue
                
            if user_input.lower() == '/clear':
                context_history = []
                print("✨ Historique de session effacé.")
                continue

            # Build simple context from history
            context_str = ""
            if context_history:
                # Keep last 6 exchanges for context
                recent = context_history[-12:]
                context_str = "HISTORIQUE RÉCENT :\n" + "\n".join(recent)

            print("🤖 MiMo réfléchit...", end="\r")
            result = await client.generate(user_input, context=context_str if context_str else None)
            
            if result.success:
                # Clear "Thinking..."
                print(" " * 30, end="\r")
                print(f"🤖 MiMo > {result.code}")
                
                # Update history
                context_history.append(f"Utilisateur: {user_input}")
                context_history.append(f"MiMo: {result.code}")
                
                # Record cost silently
                record_cost(
                    provider="mimo",
                    workflow_type="CLI_CHAT",
                    step_id="chat_turn",
                    task_id="cli_session",
                    cost_usd=result.cost_usd,
                    tokens_total=result.tokens_used,
                    tokens_input=result.input_tokens,
                    tokens_output=result.output_tokens,
                    execution_time_ms=result.execution_time_ms
                )
                # Auto-save tracker
                get_cost_tracker().save()
            else:
                print(f"\n❌ Erreur MiMo: {result.error}")
                
        except KeyboardInterrupt:
            print("\n")
            break
        except Exception as e:
            print(f"\n❌ Erreur imprévue: {e}")

    await client.close()
    print("\n👋 Au revoir !")

if __name__ == "__main__":
    # If called with 'status' argument, just show monitor
    if len(sys.argv) > 1 and sys.argv[1] == "status":
        show_mimo_status()
    else:
        try:
            asyncio.run(chat())
        except KeyboardInterrupt:
            pass
