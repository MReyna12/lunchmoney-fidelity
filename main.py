import requests
import settings
import argparse
import pandas
import datetime

# Todo:
# Figure out how to automate the downloading of the CSV from fidelity and renaming the file to investments.csv and storing in the scripts folder.
# Figure out where I can use try / except statements
# Maybe add tests
# Turn into nightly job
# Add README
# Add setup.cfg
# Add .gitignore

headers = {"Authorization": f"Bearer {settings.LUNCHMONEY_API_TOKEN}"}


def get_fidelity_tag_id(tag_name: str) -> str:
    tags_response = requests.get("https://dev.lunchmoney.app/v1/tags", headers=headers)
    tags_data = tags_response.json()
    fidelity_tag_id = None
    for tag in tags_data:
        if tag["name"] == tag_name:
            fidelity_tag_id = tag["id"]
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
        "https://dev.lunchmoney.app/v1/transactions", headers=headers, params=payload
    )
    fidelity_transactions_data = fidelity_transactions_response.json()
    return fidelity_transactions_data


def update_fidelity_transactions(current_transactions: dict) -> None:
    df = pandas.read_csv("investments.csv")
    current_date = datetime.date.today().strftime("%Y-%m-%d")
    for transaction in current_transactions["transactions"]:
        if transaction["payee"] and transaction["notes"] in df.values:
            test_something = df.loc[
                (df["Account Name"] == transaction["payee"])
                & (df["Description"] == transaction["notes"])
            ]
            current_amount = test_something["Current Value"].values[0].replace("$", "-")
            payload = {
                "transaction": {"date": current_date, "amount": current_amount}
            }
            transaction_id = transaction["id"]
            requests.put(
                "https://dev.lunchmoney.app/v1/transactions/{}".format(transaction_id),
                headers=headers,
                json=payload,
            )


def update_investment_balance(updated_transactions: dict) -> None:
    # Potentially refactor this new_balance logic.
    new_balance = 0
    for transaction in updated_transactions["transactions"]:
        transaction_amount = transaction["amount"].replace("-", "")
        new_balance += float(transaction_amount)
    new_balance = round(new_balance, 2)
    new_balance = str(new_balance)

    if new_balance != "0":
        asset_response = requests.get(
            "https://dev.lunchmoney.app/v1/assets", headers=headers
        )
        asset_data = asset_response.json()
        asset_id = asset_data["assets"][0]["id"]
        payload = {"assets": {"balance": new_balance}}
        requests.put(
            "https://dev.lunchmoney.app/v1/assets/{}".format(asset_id),
            headers=headers,
            json=payload,
        )


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

    args = parser.parse_args()
    tag_name = args.tag_name
    start_date = args.start_date
    end_date = args.end_date

    tag_id = get_fidelity_tag_id(tag_name)
    current_transactions = get_transactions_by_date_and_tag_id(
        start_date, end_date, tag_id
    )
    update_fidelity_transactions(current_transactions)
    updated_transactions = get_transactions_by_date_and_tag_id(
        start_date, end_date, tag_id
    )
    update_investment_balance(updated_transactions)


if __name__ == "__main__":
    main()
