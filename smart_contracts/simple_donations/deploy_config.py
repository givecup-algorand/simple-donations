import logging
from algosdk.v2client.algod import AlgodClient
from algosdk.v2client.indexer import IndexerClient
import algokit_utils

from smart_contracts.artifacts.give_cup_donations.client import GiveCupDonationsClient

logger = logging.getLogger(__name__)

# Define deployment behavior based on supplied app spec
def deploy(
    algod_client: AlgodClient,
    indexer_client: IndexerClient,
    app_spec: algokit_utils.ApplicationSpecification,
    deployer: algokit_utils.Account,
) -> None:
    # Initialize the GiveCupDonations client
    app_client = GiveCupDonationsClient(
        algod_client,
        creator=deployer,
        indexer_client=indexer_client,
    )

    # Deploy the smart contract
    app_client.deploy(
        on_schema_break=algokit_utils.OnSchemaBreak.AppendApp,
        on_update=algokit_utils.OnUpdate.AppendApp,
    )

    # Example of interacting with the deployed smart contract
    # In this case, querying the total number of donations
    total_donations = app_client.get_total_donations()
    logger.info(
        f"Queried total donations on {app_spec.contract.name} ({app_client.app_id}), "
        f"received: {total_donations.return_value}"
    )
