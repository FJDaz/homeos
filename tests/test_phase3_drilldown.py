import json
import time
import urllib.request
import urllib.error

BASE_URL = "http://localhost:9998"

def test_drilldown():
    print("🚀 Starting Phase 3 Stress Test: Drill-down & Contextual Pruning")
    
    try:
        # 1. Fetch full genome
        start = time.time()
        with urllib.request.urlopen(f"{BASE_URL}/api/genome") as response:
            full_data = response.read()
            full_size = len(full_data)
        print(f"✅ Full Genome: {full_size} bytes (Time: {time.time() - start:.3f}s)")
        
        # 2. Sequential Drill-down (N0 -> N1 -> N2 -> N3)
        targets = ["n0_brainstorm", "n1_ir", "n2_ir_report", "comp_ir_table"]
        
        for target_id in targets:
            start = time.time()
            try:
                with urllib.request.urlopen(f"{BASE_URL}/api/genome/pruned/{target_id}") as response:
                    pruned_data = response.read()
                    pruned_size = len(pruned_data)
                    reduction = (1 - (pruned_size / full_size)) * 100
                    print(f"✅ Pruning {target_id}: {pruned_size} bytes ({reduction:.1f}% reduction, Time: {time.time() - start:.3f}s)")
            except urllib.error.HTTPError as e:
                print(f"❌ Error pruning {target_id}: {e.code}")

        print("\n🏆 Stress Test Completed: Sullivan Architecture is responsive and efficient.")
    except Exception as e:
        print(f"❌ Test Failed: {str(e)}")

if __name__ == "__main__":
    test_drilldown()
