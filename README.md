🌍 EarthQuakeWatch GCP

EarthQuakeWatch GCP არის სეისმური მონაცემების მონიტორინგის პლატფორმა, რომელიც აერთიანებს Flask API-ს, MySQL კატალოგს და Google Cloud Platform-ის სერვისებს.
პროექტი აჩვენებს end-to-end data pipeline-ს: მონაცემების ingestion → შენახვა → ანალიტიკა → ვიზუალიზაცია.

🚀 Features

Hourly Data Ingestion: Python script იღებს მიწისძვრის ახალ ჩანაწერებს MySQL კატალოგიდან ყოველ 1 საათში.

Datastore Storage: მოვლენები ინახება Google Cloud Datastore-ში.

ETL to BigQuery: Cloud Function აგზავნის მონაცემებს BigQuery-ში ანალიტიკისთვის.

Analytics with BigQuery: Query-ებით ითვლება სტატისტიკა (მაგ. ბოლო 24 საათის საშუალო magnitude).

Flask API (App Engine):

/events → ბოლო მიწისძვრების სია Datastore-დან

/stats → ანალიტიკა BigQuery-დან

Dashboard: Flask + Chart.js/Plotly → გრაფიკები და ვიზუალიზაციები.

🛠️ Tech Stack

Backend: Python, Flask

Databases: MySQL (source), Google Datastore (operational), BigQuery (analytics)

Cloud Services: App Engine, Cloud Functions, Cloud Scheduler, Pub/Sub

Visualization: Chart.js / Plotly

📐 Architecture
MySQL (Earthquake Catalog)
        ⬇ (Hourly Python Script / Cloud Scheduler)
Datastore (Operational DB)
        ⬇ (Cloud Function ETL)
BigQuery (Analytics DB)
        ⬇
Flask API (App Engine)
        ⬆
Chart.js Dashboard (Visualization)
