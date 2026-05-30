"""Seed database with sample data"""
import sys
import argparse
from datetime import datetime, timedelta
import random


def create_sample_templates():
    """Tạo mẫu template"""
    return [
        {
            "product_type": "PCB-A001",
            "required_components": ["R1", "R2", "C1", "C2", "IC1", "LED1", "LED2", "Q1"],
            "component_positions": {
                "R1": {"x": 100, "y": 150, "w": 40, "h": 20},
                "R2": {"x": 200, "y": 150, "w": 40, "h": 20},
                "C1": {"x": 150, "y": 250, "w": 30, "h": 30},
                "C2": {"x": 250, "y": 250, "w": 30, "h": 30},
                "IC1": {"x": 300, "y": 200, "w": 60, "h": 40},
                "LED1": {"x": 400, "y": 100, "w": 15, "h": 15},
                "LED2": {"x": 450, "y": 100, "w": 15, "h": 15},
                "Q1": {"x": 350, "y": 300, "w": 25, "h": 35},
            },
            "antenna_position": {"x": 500, "y": 50, "angle": 0},
            "sn_format": r"^[A-Z]{2}\d{6}$",
            "qr_format": r"^PCB-[A-Z0-9]+-\d{4}$",
        },
        {
            "product_type": "PCB-B002",
            "required_components": ["R1", "R2", "R3", "C1", "IC1", "IC2", "CONN1"],
            "component_positions": {
                "R1": {"x": 80, "y": 120, "w": 35, "h": 18},
                "R2": {"x": 180, "y": 120, "w": 35, "h": 18},
                "R3": {"x": 280, "y": 120, "w": 35, "h": 18},
                "C1": {"x": 130, "y": 220, "w": 28, "h": 28},
                "IC1": {"x": 250, "y": 180, "w": 55, "h": 38},
                "IC2": {"x": 400, "y": 180, "w": 45, "h": 30},
                "CONN1": {"x": 50, "y": 300, "w": 80, "h": 40},
            },
            "antenna_position": {"x": 480, "y": 40, "angle": 45},
            "sn_format": r"^SN-\d{8}$",
            "qr_format": r"^PCB-B002-\d{4}$",
        },
    ]


def create_sample_inspections(count=20):
    """Tạo mẫu kết quả kiểm tra"""
    products = ["PCB-A001", "PCB-B002"]
    stations = ["STATION-01", "STATION-02", "STATION-03"]
    results = ["PASS"] * 85 + ["FAIL"] * 15  # 85% pass rate

    inspections = []
    for i in range(count):
        product = random.choice(products)
        result = random.choice(results)
        now = datetime.now() - timedelta(hours=random.randint(0, 72))

        missing = []
        qr_result = "PASS"
        sn_result = "PASS"
        anten_result = "PASS"

        if result == "FAIL":
            fail_type = random.choice(["component", "qr", "sn", "anten"])
            if fail_type == "component":
                missing = random.sample(["R1", "R2", "C1", "LED1", "Q1"], k=random.randint(1, 2))
            elif fail_type == "qr":
                qr_result = "FAIL"
            elif fail_type == "sn":
                sn_result = "FAIL"
            else:
                anten_result = "FAIL"

        inspections.append({
            "product_serial": f"SN{1000 + i:06d}",
            "product_type": product,
            "batch_number": f"BATCH-{random.randint(1, 5):03d}",
            "station_id": random.choice(stations),
            "overall_result": result,
            "missing_components": missing,
            "qr_result": qr_result,
            "sn_result": sn_result,
            "antenna_result": anten_result,
            "inference_time_ms": round(random.uniform(100, 350), 2),
            "inspection_time": now.isoformat(),
        })

    return inspections


def main():
    parser = argparse.ArgumentParser(description="Seed database with sample data")
    parser.add_argument("--dry-run", action="store_true", help="Show data without inserting")
    parser.add_argument("--count", type=int, default=20, help="Number of inspections")
    args = parser.parse_args()

    print("🌱 Seeding database...")

    templates = create_sample_templates()
    inspections = create_sample_inspections(args.count)

    print(f"\n📋 Templates: {len(templates)}")
    for t in templates:
        print(f"  - {t['product_type']}: {len(t['required_components'])} components")

    print(f"\n🔍 Inspections: {len(inspections)}")
    passed = sum(1 for i in inspections if i["overall_result"] == "PASS")
    failed = len(inspections) - passed
    print(f"  - PASS: {passed} ({passed/len(inspections)*100:.1f}%)")
    print(f"  - FAIL: {failed} ({failed/len(inspections)*100:.1f}%)")

    if args.dry_run:
        print("\n⚠️  DRY RUN — no data inserted")
        return

    print("\n✅ Seed data ready (implement DB insertion when models are connected)")


if __name__ == "__main__":
    main()
