import asyncio, logging, yaml, os
from fastapi import FastAPI, HTTPException, Query
from app.database import SessionLocal, Lead, Base, ENGINE, init_db
from app.plugin_loader import autodiscover
from app.scorer import Scorer
from app.outreach import generate_text, craigslists_email_prompt, salesnav_inmail_prompt, send_gmail
from sqlalchemy.exc import IntegrityError
from sqlalchemy import func

logging.basicConfig(level=logging.INFO)
app = FastAPI(title="Sumeru Lead-Gen API")

# --- load config once
with open("config.yaml", "r") as f:
    CFG = yaml.safe_load(f)
SCORER = Scorer(CFG)

# --- bootstrap plugins
PLUGINS = autodiscover()
logging.info("Loaded plugins: %s", [p.name for p in PLUGINS])

# --- DB init
init_db()  # Use the new init_db function with retry logic

# --- util

def upsert_lead(db, lead_dict):
    lead = Lead(**lead_dict)
    try:
        db.add(lead)
        db.commit()
    except IntegrityError:
        db.rollback()  # duplicate – ignore
        return None
    return lead

# --- worker loop
async def poll_plugins_interval(seconds=60):
    while True:
        logging.info("Scraping cycle start…")
        db = SessionLocal()
        for plugin in PLUGINS:
            for raw in plugin.fetch():
                rec, con, rel, tot, status = SCORER.compute(raw)
                raw.update(dict(recency_score=rec, contact_score=con,
                                relevance=rel, total_score=tot, status=status))
                lead = upsert_lead(db, raw)
                if lead and status == "Hot":
                    queue_hot_email(db, lead)
        db.close()
        logging.info("Cycle done. Sleeping %s s…", seconds)
        await asyncio.sleep(seconds)


def queue_hot_email(db, lead: Lead):
    if lead.source == "craigslist" and lead.email:
        prompt = craigslists_email_prompt(lead.__dict__)
        text, model = generate_text(prompt)
        subject = f"Let's ship your {lead.title.split()[0]} in record time"
        send_gmail(lead.email, subject, text)
        lead.thread_id = f"email:{subject[:20]}"
        lead.model_version = model
        lead.status = "emailed"
        db.commit()
    elif lead.source == "salesnav":
        prompt = salesnav_inmail_prompt(lead.__dict__)
        text, model = generate_text(prompt)
        lead.thread_id = text[:32]
        lead.model_version = model
        lead.status = "emailed"
        db.commit()

# background task
@app.on_event("startup")
async def startup_event():
    asyncio.create_task(poll_plugins_interval())

# --- REST endpoints
@app.get("/leads")
def get_leads(status: str | None = Query(default=None)):
    db = SessionLocal()
    q = db.query(Lead)
    if status:
        q = q.filter(Lead.status == status)
    return q.order_by(Lead.id.desc()).limit(200).all()

@app.get("/queue/hot")
def queue_hot():
    db = SessionLocal()
    return db.query(Lead).filter(Lead.status == "Hot").all()

@app.get("/stats")
def stats():
    db = SessionLocal()
    total = db.query(func.count(Lead.id)).scalar()
    hot = db.query(func.count(Lead.id)).filter(Lead.status == "Hot").scalar()
    warm = db.query(func.count(Lead.id)).filter(Lead.status == "Warm").scalar()
    cold = db.query(func.count(Lead.id)).filter(Lead.status == "Cold").scalar()
    avg = db.query(func.avg(Lead.total_score)).scalar() or 0
    return {"total": total, "hot": hot, "warm": warm, "cold": cold, "avg_score": round(avg,2)} 