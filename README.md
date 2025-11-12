🌍 EarthQuakeWatch AWS
EarthQuakeWatch is a seismic data monitoring and analytics platform that integrates a Flask REST API, a MySQL catalog, and Amazon Web Services (AWS) cloud infrastructure.
It demonstrates a complete end-to-end data pipeline — from ingestion to analytics and visualization.

🧭 Overview
EarthQuakeWatch automatically collects and analyzes earthquake data from a central MySQL catalog.
It performs:

1.Ingestion → Hourly data extraction from MySQL
2.Storage → Real-time storage in DynamoDB
3.ETL Processing → AWS Lambda sends cleaned data to S3 for analytics
4.Analytics → Amazon Athena computes real-time statistics
5.Visualization → Flask + Chart.js dashboard displays live results

🚀 Features
Feature	Description
⏱️ Hourly Data Ingestion - AWS EventBridge Scheduler triggers a Python script every hour
🗄️ Operational Storage (DynamoDB) - All seismic events are stored in DynamoDB for fast access
⚙️ ETL via Lambda - AWS Lambda transforms and uploads data to S3
📊 Analytics with Athena - SQL-like analytics using Athena queries on S3 data
🧠 Flask REST API -     /events → list of recent earthquakes 
                        /stats → statistical insights from Athena
📈 Visualization Dashboard - Flask + Chart.js / Plotly dashboard for visual analytics
🔐 API Key Authentication - Internal ingestion endpoints secured by X-API-Key header


🧩 System Architecture
MySQL (Earthquake Catalog)
        ⬇  (Python Script / EventBridge Scheduler)
DynamoDB (Operational DB)
        ⬇  (AWS Lambda ETL)
S3 + Athena (Analytics Layer)
        ⬇
Flask API (Elastic Beanstalk / ECS)
        ⬆
Chart.js / Plotly Dashboard (Visualization)

🛠️ Tech Stack
Backend:
        Python, Flask-RESTx, SQLAlchemy
        boto3 (AWS SDK for Python)

Databases:
        MySQL (source catalog, AWS RDS)
        DynamoDB (operational store)
        Amazon Athena / Redshift (analytics)

AWS Services:
        Elastic Beanstalk (Flask API hosting)
        Lambda (ETL functions)
        EventBridge Scheduler (hourly jobs)
        S3 (data storage)
        SNS / SQS (optional message queues)

Visualization:
        Chart.js / Plotly
        Jinja2 templates via Flask

🔒 Security
        API Key Auth: X-API-Key header for ingestion routes
        Environment Configuration: secrets loaded from .env
        AWS IAM Roles: secure service-level permissions for Lambda, Beanstalk, and S3

🧠 Future Improvements
        ✅ Caching layer with AWS ElastiCache (Redis)
        ✅ Real-time updates via WebSocket (API Gateway)
        ✅ ML-based event clustering using SageMaker
        ✅ Modern React Dashboard front-end