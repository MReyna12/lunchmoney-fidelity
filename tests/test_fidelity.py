# Need to update my requirements.txt
from investments import main
import pytest


def test_get_fidelity_tag_id(requests_mock):
    mock_json = [
        {
            "id": 1,
            "name": "faketag",
        }
    ]

    fake_tag = "faketag"

    requests_mock.get("https://dev.lunchmoney.app/v1/tags", json=mock_json)

    tag_id = main.get_fidelity_tag_id(fake_tag)

    assert tag_id == 1
    assert requests_mock.call_count == 1
    assert requests_mock.request_history[0].method == "GET"


def test_get_transactions_by_date_and_tag_id(requests_mock):
    mock_json = {
        "transactions": [
            {
                "id": 1,
                "payee": "Bank",
                "notes": "Account",
            },
            {
                "id": 2,
                "payee": "Bank",
                "notes": "Account",
            },
            {
                "id": 3,
                "payee": "Bank",
                "notes": "Account",
            },
            {
                "id": 4,
                "payee": "Bank",
                "notes": "Account",
            },
            {
                "id": 5,
                "payee": "Bank",
                "notes": "Accpimt",
            },
            {
                "id": 6,
                "payee": "Bank",
                "notes": "Account",
            },
            {
                "id": 7,
                "payee": "Bank",
                "notes": "Account",
            },
            {
                "id": 8,
                "payee": "Bank",
                "notes": "Account",
            },
            {
                "id": 9,
                "payee": "Bank",
                "notes": "Account",
            },
            {
                "id": 10,
                "payee": "Bank",
                "notes": "Account",
            },
            {
                "id": 11,
                "payee": "Bank",
                "notes": "Account",
            },
        ]
    }

    requests_mock.get("https://dev.lunchmoney.app/v1/transactions", json=mock_json)

    start_date = "2024-08-01"
    end_date = "2024-08-02"
    tag_id = "1"

    current_transactions = main.get_transactions_by_date_and_tag_id(
        start_date, end_date, tag_id
    )

    assert len(current_transactions["transactions"]) == 11
    assert requests_mock.call_count == 1
    assert requests_mock.request_history[0].method == "GET"


def test_update_fidelity_transactions(requests_mock):
    # Look at ROPE for example of how to mock out the relevant data for the CSV
    current_transactions = {
        "transactions": [
            {
                "id": 1,
                "payee": "Bank",
                "notes": "Account",
            },
            {
                "id": 2,
                "payee": "Bank",
                "notes": "Account",
            },
            {
                "id": 3,
                "payee": "Bank",
                "notes": "Account",
            },
            {
                "id": 4,
                "payee": "Bank",
                "notes": "Account",
            },
            {
                "id": 5,
                "payee": "Bank",
                "notes": "Account",
            },
            {
                "id": 6,
                "payee": "Bank",
                "notes": "Account",
            },
            {
                "id": 7,
                "payee": "Bank",
                "notes": "Account",
            },
            {
                "id": 8,
                "payee": "Bank",
                "notes": "Account",
            },
            {
                "id": 9,
                "payee": "Bank",
                "notes": "Account",
            },
            {
                "id": 10,
                "payee": "Bank",
                "notes": "Account",
            },
            {
                "id": 11,
                "payee": "Bank",
                "notes": "Account",
            },
        ]
    }

    csv_path = "/Users/mr110/Downloads/investments.csv"


def test_get_fidelity_asset_id(requests_mock):
    mock_json = {"assets": [{"id": 1}]}

    requests_mock.get("https://dev.lunchmoney.app/v1/assets", json=mock_json)

    asset_id = main.get_fidelity_asset_id()

    assert asset_id == 1
    assert requests_mock.call_count == 1
    assert requests_mock.request_history[0].method == "GET"


def test_update_investment_balance(requests_mock, mocker):
    updated_transactions = {
        "transactions": [
            {"id": 1, "payee": "Bank", "notes": "Account", "amount": "-12345.5555"},
            {"id": 2, "payee": "Bank", "notes": "Account", "amount": "-12345.5555"},
            {"id": 3, "payee": "Bank", "notes": "Account", "amount": "-12345.5555"},
            {"id": 4, "payee": "Bank", "notes": "Account", "amount": "-12345.5555"},
            {"id": 5, "payee": "Bank", "notes": "Account", "amount": "-12345.5555"},
            {"id": 6, "payee": "Bank", "notes": "Account", "amount": "-12345.5555"},
            {"id": 7, "payee": "Bank", "notes": "Account", "amount": "-12345.5555"},
            {"id": 8, "payee": "Bank", "notes": "Account", "amount": "-12345.5555"},
            {"id": 9, "payee": "Bank", "notes": "Account", "amount": "-12345.5555"},
            {"id": 10, "payee": "Bank", "notes": "Account", "amount": "-12345.5555"},
            {"id": 11, "payee": "Bank", "notes": "Account", "amount": "-12345.5555"},
        ]
    }

    mocker.patch("investments.main.get_fidelity_asset_id", return_value=1)

    asset_id = 1

    requests_mock.put("https://dev.lunchmoney.app/v1/assets/{}".format(asset_id))

    main.update_investment_balance(updated_transactions)

    new_total_investment_amount = requests_mock.last_request.json()

    assert requests_mock.call_count == 1
    assert requests_mock.request_history[0].method == "PUT"
    assert new_total_investment_amount["balance"] == "135801.11"
