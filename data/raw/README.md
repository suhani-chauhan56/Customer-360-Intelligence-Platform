# Raw Data Manifest

Raw CSV files are intentionally excluded from Git because the complete input set is large. Download the three source datasets, preserve the Olist filenames listed below, and place every required file in this directory.

| Source | Required local filename |
|---|---|
| Olist Brazilian E-Commerce | `olist_customers_dataset.csv` |
| Olist Brazilian E-Commerce | `olist_orders_dataset.csv` |
| Olist Brazilian E-Commerce | `olist_order_items_dataset.csv` |
| Olist Brazilian E-Commerce | `olist_order_payments_dataset.csv` |
| Olist Brazilian E-Commerce | `olist_order_reviews_dataset.csv` |
| Olist Brazilian E-Commerce | `olist_products_dataset.csv` |
| Olist Brazilian E-Commerce | `product_category_name_translation.csv` |
| E-Commerce Events History in Cosmetics Shop | `ecommerce_events_2019_dec.csv` |
| Datafiniti Amazon Consumer Reviews | `amazon_consumer_reviews.csv` |

`olist_geolocation_dataset.csv` and `olist_sellers_dataset.csv` are not required because the current warehouse and analytical questions do not use them.

Notebook `01_Data_Audit.ipynb` validates this manifest before any ETL work begins.
