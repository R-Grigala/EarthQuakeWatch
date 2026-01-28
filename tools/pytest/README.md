# Pytest ინსტრუქცია (`tools/pytest`)

ამ ფოლდერში ინახება ყველა ტესტი, რომელიც Flask API-სა და ინფრასტრუქტურის (DB, AWS) ქცევას ამოწმებს.

## სტრუქტურა

- `conftest.py`  
  შეიცავს საერთო pytest fixture-ებს:
  - `app` – ქმნის Flask აპს `TestConfig`-ით და დროებით SQLite DB ფაილით.
  - `client` – `app.test_client()` HTTP რეიკვესტებისთვის.
  - `runner` – `app.test_cli_runner()` CLI command-ების ტესტირებისთვის.

- `api/`  
  - `test_api_events.py` – ტესტავს `/api/events` endpoint-ს (GET + POST, API key).
  - `test_api_stats.py` – ტესტავს `/api/stats` endpoint-ს (ცარიელი / შევსებული DB).

- `aws/`  
  - AWS/MySQL დაკავშირებული ტესტების ადგილი (მაგ. `awsDB_connection.py`).

## როგორ იქმნება ტესტური DB

`conftest.py` → `app` fixture:

1. ქმნის დროებით SQLite ფაილს (თითო ტესტ სესიაზე).
2. ქმნის Flask აპს `TestConfig`-ით.
3. `app.app_context()`-ში იძახებს `init_db_core()`-ს (`src/commands.py`), რომელიც:
   - `db.drop_all()` + `db.create_all()` – თავიდან ქმნის schema-ს.
4. დამატებით, `populate_db_core()` ერთი საკონტროლო `SeismicEvent` ჩანაწერს ამატებს, რომელსაც stats ტესტები იყენებს.

ამრიგად:
- API ტესტები ყოველთვის სუფთა, ცალკე SQLite ბაზაზე chạy-დებიან.
- production CLI command-ები (`flask init_db`, `flask populate_db`) იყენებენ იმავე core ლოგიკას, მაგრამ pytest-ში **არ იძახებენ Click-ს** (არ არის კონფლიქტი `-v` და სხვა options-თან).

## ტესტების გაშვება

პროექტის root-დან:

- ყველა pytest ტესტი:

```bash
cd /home/sysop/Code/EarthQuakeWatch
pytest tools/pytest -vv
```

- მხოლოდ Events API ტესტები:

```bash
pytest tools/pytest/api/test_api_events.py -vv
```

- მხოლოდ Stats API ტესტები:

```bash
pytest tools/pytest/api/test_api_stats.py -vv
```

## როგორ დავამატოთ ახალი ტესტი

1. შექმენი ახალი ფაილი `test_*.py` სახელით შესაბამის ქვეფოლდერში (`api/`, `aws/` და ა.შ.).
2. გამოიყენე უკვე არსებული fixture-ები:
   - `client` – HTTP ტესტებისთვის.
   - `app` – თუ გჭირდება `app.app_context()` და ORM-ით პირდაპირ ჩაწერა/წაკითხვა.
3. თუ კიდევ გჭირდება სპეციალური seed მონაცემები:
   - ან გამოიყენე `populate_db_core()` `app.app_context()`-ში,
   - ან ტესტის შიგნით შექმენი საკუთარი `SeismicEvent` და `create()`/`save()` გამოიძახე.

