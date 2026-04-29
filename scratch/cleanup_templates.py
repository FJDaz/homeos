import os
import subprocess

TEMPLATE_DIR = "Frontend/3. STENCILER/static/templates"
KEEP_LIST = [
    "login.html",
    "workspace.html",
    "student_login.html",
    "teacher_dashboard.html",
    "bkd_frd.html",
    "cadrage_alt.html",
    "cadrage_prof.html",
    "frd_editor.html",
    "brainstorm_war_room_tw.html",
    "intent_viewer.html"
]

def cleanup():
    # Get all html files in the templates directory recursively
    # (Since there are subdirectories like _archive and zip_dist_*)
    files_to_check = []
    for root, dirs, files in os.walk(TEMPLATE_DIR):
        for f in files:
            if f.endswith(".html"):
                full_path = os.path.join(root, f)
                files_to_check.append(full_path)

    files_to_remove = []
    for f_path in files_to_check:
        filename = os.path.basename(f_path)
        if filename not in KEEP_LIST:
            files_to_remove.append(f_path)

    if not files_to_remove:
        print("No files to remove.")
        return

    print(f"Found {len(files_to_remove)} files to remove.")
    for f_path in files_to_remove:
        print(f"Removing: {f_path}")
        # Use git rm -rf to handle directories if needed, but here we have full paths to files
        subprocess.run(["git", "rm", "-f", f_path], check=False)

    # Also remove the subdirectories if they are empty or contain only non-html files we want to remove
    # But for now, let's just do what the roadmap asked.
    # The roadmap said "Supprimer tout le reste dans static/templates/"
    
    # Let's also check for non-html files that should be removed if they are not the manifest
    # Actually, let's just stick to the roadmap's "Lister tous les html" rule for now.

if __name__ == "__main__":
    cleanup()
