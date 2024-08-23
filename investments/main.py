import requests
import settings
import argparse
import pandas
import datetime


HEADER = {"Authorization": f"Bearer {settings.LUNCHMONEY_API_TOKEN}"}


def get_fidelity_tag_id(tag_name: str) -> str:
    tags_response = requests.get("https://dev.lunchmoney.app/v1/tags", headers=HEADER)
    tags_response.raise_for_status()
    tags_data = tags_response.json()
    fidelity_tag_id = None
    for tag in tags_data:
        if tag["name"] == tag_name:
            fidelity_tag_id = tag["id"]
    if fidelity_tag_id is None:
        raise TypeError("The return value for fidelity_tag_id cannot be None")
    return fidelity_tag_id


def validate_date_format(input: str) -> datetime.datetime:
    try:
        return datetime.datetime.strptime(input, "%Y-%m-%d")
    except ValueError:
        raise argparse.ArgumentTypeError(
            f"This is not a valid date: {input}. Please use this format YYYY-MM-DD."
        )


def get_transactions_by_date_and_tag_id(
    start_date: str, end_date: str, tag_id: str
) -> dict:
    payload = {
        "start_date": start_date,
        "end_date": end_date,
        "tag_id": tag_id,
    }
    fidelity_transactions_response = requests.get(
        "https://dev.lunchmoney.app/v1/transactions",
        headers=HEADER,
        params=payload,
    )
    fidelity_transactions_response.raise_for_status()
    fidelity_transactions_data = fidelity_transactions_response.json()
    return fidelity_transactions_data


def update_fidelity_transactions(current_transactions: dict, csv_path: str) -> None:
    df = pandas.read_csv(csv_path)
    current_date = datetime.date.today().strftime("%Y-%m-%d")
    for transaction in current_transactions["transactions"]:
        if transaction["payee"] and transaction["notes"] in df.values:
            investment_account = df.loc[
                (df["Account Name"] == transaction["payee"])
                & (df["Description"] == transaction["notes"])
            ]
            current_amount = investment_account["Current Value"].values[0].replace("$", "-")
            payload = {"transaction": {"date": current_date, "amount": current_amount}}
            transaction_id = transaction["id"]
            updated_transactions_response = requests.put(
                "https://dev.lunchmoney.app/v1/transactions/{}".format(transaction_id),
                headers=HEADER,
                json=payload,
            )
            updated_transactions_response.raise_for_status()


def get_fidelity_asset_id() -> int:
    asset_response = requests.get(
        "https://dev.lunchmoney.app/v1/assets", headers=HEADER
    )
    asset_response.raise_for_status()
    asset_data = asset_response.json()
    asset_id = asset_data["assets"][0]["id"]
    return asset_id


def update_investment_balance(updated_transactions: dict) -> None:
    new_balance = 0
    for transaction in updated_transactions["transactions"]:
        transaction_amount = transaction["amount"].replace("-", "")
        new_balance += float(transaction_amount)
    new_balance = round(new_balance, 2)
    new_balance = str(new_balance)

    if new_balance != "0":
        payload = {"balance": new_balance}
        asset_id = get_fidelity_asset_id()
        updated_asset_response = requests.put(
            "https://dev.lunchmoney.app/v1/assets/{}".format(asset_id),
            headers=HEADER,
            json=payload,
        )
        updated_asset_response.raise_for_status()


def main():
    parser = argparse.ArgumentParser(description="Some description goes here")
    parser.add_argument(
        "tag_name", type=str, help="Name of the tag to be used to retrieve the tag_id"
    )
    parser.add_argument(
        "start_date",
        type=validate_date_format,
        help="Denotes the beginning of the time period to fetch transactions for. Format: YYYY-MM-DD. Cannot be same date as end_date.",
    )
    parser.add_argument(
        "end_date",
        type=validate_date_format,
        help="Denotes the end of the time period you'd like to get transactions for. Format: YYYY-MM-DD. Cannot be the same date as start_date",
    )
    parser.add_argument(
        "path",
        type=str,
        help="Path to CSV file containing various investment accounts and their balances",
    )

    args = parser.parse_args()
    tag_name = args.tag_name
    start_date = args.start_date
    end_date = args.end_date
    csv = args.path

    try:
        tag_id = get_fidelity_tag_id(tag_name)
        current_transactions = get_transactions_by_date_and_tag_id(
            start_date, end_date, tag_id
        )
        update_fidelity_transactions(current_transactions, csv_path=csv)
        updated_transactions = get_transactions_by_date_and_tag_id(
            start_date, end_date, tag_id
        )
        update_investment_balance(updated_transactions)
    except requests.exceptions.HTTPError as httperr:
        raise httperr
    except requests.exceptions.ConnectionError as connerr:
        raise connerr
    except requests.exceptions.RequestException as err:
        raise err


if __name__ == "__main__":
    main()
