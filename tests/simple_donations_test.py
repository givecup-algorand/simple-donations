import pytest
from algokit_utils import (
    ApplicationClient,
    ApplicationSpecification,
    get_localnet_default_account,
)
from algosdk.v2client.algod import AlgodClient

from smart_contracts.simple_donations import contract as simple_donations_contract


@pytest.fixture(scope="session")
def simple_donations_app_spec(algod_client: AlgodClient) -> ApplicationSpecification:
    return simple_donations_contract.app.build(algod_client)


@pytest.fixture(scope="session")
def simple_donations_client(
    algod_client: AlgodClient, simple_donations_app_spec: ApplicationSpecification
) -> ApplicationClient:
    client = ApplicationClient(
        algod_client,
        app_spec=simple_donations_app_spec,
        signer=get_localnet_default_account(algod_client),
    )
    client.create()
    return client


def test_says_hello(simple_donations_client: ApplicationClient) -> None:
    result = simple_donations_client.call(simple_donations_contract.hello, name="World")

    assert result.return_value == "Hello, World"
