from datetime import datetime, timedelta
from typing import List

class Scorer:
    def __init__(self, cfg: dict):
        self.cfg = cfg
        self.kw = [k.lower() for k in cfg["keywords"]]
        self.neg_kw = [k.lower() for k in cfg["negative_keywords"]]
        self.recency_points = cfg["scoring"]["recency_points"]
        self.recency_hours = cfg["scoring"]["recency_hours"]
        self.contact_weights = cfg["scoring"]["contact"]
        self.rel_per_hit = cfg["scoring"]["relevance"]["per_hit"]
        self.rel_cap = cfg["scoring"]["relevance"]["max"]
        self.thresholds = cfg["status_thresholds"]

    def compute(self, lead: dict):
        # --- recency
        if not lead.get("posted_at"):
            recency_score = 0
        else:
            delta = datetime.utcnow() - lead["posted_at"]
            recency_score = self.recency_points if delta <= timedelta(hours=self.recency_hours) else 0
        # --- contact
        contact_score = sum([
            self.contact_weights["phone"] if lead.get("phone") else 0,
            self.contact_weights["email"] if lead.get("email") else 0,
            self.contact_weights["name"] if lead.get("contact_name") else 0,
            self.contact_weights["rate"] if lead.get("rate") else 0,
        ])
        # --- relevance
        body = f"{lead.get('title','')} {lead.get('body','')}".lower()
        if any(neg in body for neg in self.neg_kw):
            relevance = 0
        else:
            hits = sum(body.count(k) for k in self.kw)
            relevance = min(hits * self.rel_per_hit, self.rel_cap)
        total = recency_score + contact_score + relevance
        if total >= self.thresholds["hot"]:
            status = "Hot"
        elif total >= self.thresholds["warm"]:
            status = "Warm"
        else:
            status = "Cold"
        return recency_score, contact_score, relevance, total, status 