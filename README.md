# Sumeru Digital – Lead-Gen Pipeline 🚀

One-click scrape, score & outreach for Craigslist + LinkedIn Sales Navigator.

```bash
# clone & config
cp .env.example .env
vim .env                # 🔑 add secrets

# run
docker-compose up -d --build

# verify
curl "http://localhost:8000/stats"
curl "http://localhost:8000/leads?status=Hot"
```

### REST Cheatsheet

| Endpoint          | Verb | Purpose                               |
| ----------------- | ---- | ------------------------------------- |
| /leads?status=Hot | GET  | List leads (optionally by status)     |
| /queue/hot        | GET  | JSON array of all *Hot* leads         |
| /stats            | GET  | Total / Hot / Warm / Cold / avg score |

### Tests

Run `pytest tests/` (basic smoke tests included).

---

## 🧩 Adding New Plugins

1. `mkdir lead_plugins/my_source && touch plugin.py`
2. Implement `class Plugin(BasePlugin):` with a `name` and `fetch()` returning lead dicts.
3. Drop folder → container auto-reloads (thanks to volume mount + autodiscover).

---

### Production Notes

- Cron/poll loop defaults to 15 min; tweak in `main.py`.
- Use Amazon SES or SendGrid in place of Gmail in high-volume scenarios.
- Scale scraping via multiple worker replicas behind a queue (e.g. Celery + Redis).

---

> **That's it!** Spin it up, tail logs with `docker-compose logs -f app`, and watch fresh leads pour into MySQL 🔥 