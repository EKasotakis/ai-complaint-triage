import pandas as pd
import requests


API_URL = "http://127.0.0.1:8000/complaints"
DATA_PATH = "data/complaints.csv"


def clean_value(value):
    if pd.isna(value):
        return None

    return str(value)


def load_complaints():
    df = pd.read_csv(DATA_PATH)

    successful = 0
    failed = 0

    for _, row in df.iterrows():
        complaint = {
            "customer_name": clean_value(row["customer_name"]),
            "customer_email": clean_value(row["customer_email"]),
            "order_id": clean_value(row["order_id"]),
            "product": clean_value(row["product"]),
            "complaint_text": clean_value(row["complaint_text"]),
        }

        try:
            response = requests.post(
                API_URL,
                json=complaint,
                timeout=60,
            )

            response.raise_for_status()

            result = response.json()

            print(
                f'{result["case_id"]}: '
                f'{result["status"]}'
            )

            successful += 1

        except requests.RequestException as error:
            print(f"Request failed: {error}")
            failed += 1

    print()
    print("Batch processing complete.")
    print(f"Successful requests: {successful}")
    print(f"Failed requests: {failed}")


if __name__ == "__main__":
    load_complaints()