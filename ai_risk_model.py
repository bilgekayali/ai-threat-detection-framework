#!/usr/bin/env python3
# Conceptual AI risk scoring demo (no real data or configs)
# Author: Bilge Kayalı

import argparse
import sys
import pandas as pd
import numpy as np

def rule_score(row):
    s = 0.6*row["anomaly_score"]
    s += 0.15*row["off_hours"]
    s += 0.1*min(row["failed_logins_24h"]/10.0, 1.0)
    s += 0.1*min(row["geo_distance_km"]/5000.0, 1.0)
    s += 0.25*row["proc_injection_flag"]
    return s

def rule_risk_level(score):
    return "High" if score>0.9 else ("Medium" if score>0.6 else "Low")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", type=str, required=True, help="Path to synthetic_alerts.csv")
    ap.add_argument("--train", action="store_true", help="Train a simple model with scikit-learn (optional)")
    ap.add_argument("--score", action="store_true", help="Score rows using rules and (if available) ML")
    ap.add_argument("--out", type=str, default="results.csv", help="Output CSV for scores")
    args = ap.parse_args()

    df = pd.read_csv(args.data)

    # Base: rule-based score
    df["rule_score"] = df.apply(rule_score, axis=1)
    df["rule_risk"] = df["rule_score"].apply(rule_risk_level)

    clf = None
    used_ml = False

    if args.train or args.score:
        try:
            from sklearn.model_selection import train_test_split
            from sklearn.ensemble import GradientBoostingClassifier
            from sklearn.metrics import classification_report

            X = df[["anomaly_score","off_hours","failed_logins_24h","geo_distance_km","proc_injection_flag"]].values
            y = df["label"].values
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

            clf = GradientBoostingClassifier(random_state=42)
            clf.fit(X_train, y_train)
            y_pred = clf.predict(X_test)
            print("ML classification report (demo):")
            print(classification_report(y_test, y_pred, digits=3))
            used_ml = True

            # For scoring: blend ML proba with rule score
            probs = clf.predict_proba(df[["anomaly_score","off_hours","failed_logins_24h","geo_distance_km","proc_injection_flag"]].values)[:,1]
            df["ml_prob"] = probs
            df["blend_score"] = 0.6*df["rule_score"] + 0.4*df["ml_prob"]
            df["blend_risk"] = df["blend_score"].apply(lambda s: "High" if s>0.9 else ("Medium" if s>0.6 else "Low"))
        except Exception as e:
            print("scikit-learn not available or failed to run, falling back to rules only:", e, file=sys.stderr)

    # Choose output
    if args.score:
        if used_ml:
            out = df[["timestamp","user_id","asset_id","event_type","anomaly_score","off_hours","failed_logins_24h","geo_distance_km","proc_injection_flag","rule_score","rule_risk","ml_prob","blend_score","blend_risk"]]
        else:
            out = df[["timestamp","user_id","asset_id","event_type","anomaly_score","off_hours","failed_logins_24h","geo_distance_km","proc_injection_flag","rule_score","rule_risk"]]
        out.to_csv(args.out, index=False)
        print(f"Wrote {args.out} with risk scores.")

if __name__ == "__main__":
    main()
