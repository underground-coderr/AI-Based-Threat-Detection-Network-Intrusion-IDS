from src.ml.detection_engine import DetectionEngine

engine = DetectionEngine.get_instance()

# Simulate a normal flow
normal = {
    "SYN Flag Count": 1,
    "Flow Duration": 50000,
    "Total Fwd Packets": 10,
    "Flow Bytes/s": 1200,
    "FIN Flag Count": 1,
}

# Simulate a DoS attack
dos = {
    "SYN Flag Count": 850,
    "Flow Duration": 5000000,
    "Total Fwd Packets": 5000,
    "Flow Bytes/s": 9000000,
    "FIN Flag Count": 0,
}

print("\n--- Normal Traffic ---")
r = engine.predict(normal)
print(f"  Label      : {r['attack_type']}")
print(f"  Is Attack  : {r['is_attack']}")
print(f"  Confidence : {r['confidence']}")
print(f"  Severity   : {r['severity_label']}")

print("\n--- DoS Attack ---")
r = engine.predict(dos)
print(f"  Label      : {r['attack_type']}")
print(f"  Is Attack  : {r['is_attack']}")
print(f"  Confidence : {r['confidence']}")
print(f"  Severity   : {r['severity_label']}")
print(f"  Votes      : {r['ensemble_votes']}")