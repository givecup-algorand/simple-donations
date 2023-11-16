from beaker import Application, GlobalStateValue, LocalStateValue
from pyteal import (
    Seq, Assert, Approve, Bytes, Int, Txn, Global, TxnType, abi, TealType, Addr, If, Expr, Or
)

# Define global state for tracking donations and organizations


class GlobalState:
    donation_counter = GlobalStateValue(
        stack_type=TealType.uint64, default=Int(0))
    owner = GlobalStateValue(stack_type=TealType.bytes, default=Bytes(""))

    # Assuming a limited number of organizations for simplicity
    organizations = [GlobalStateValue(
        stack_type=TealType.bytes, default=Bytes("")) for _ in range(10)]


class LocalState:
    user_donations = LocalStateValue(
        stack_type=TealType.uint64, default=Int(0))


app = Application("GiveCupDonations", state=GlobalState())


@app.create
def create():
    return Seq(
        app.state.donation_counter.set(Int(0)),
        app.state.owner.set(Txn.sender()),  # Set the creator as the owner
        Approve()
    )


@app.external
def add_organization(organization: abi.Address) -> Expr:
    """
    Add an organization address. Only callable by the owner.
    """
    is_owner = Txn.sender() == app.state.owner

    # Logic to add an organization
    for i in range(len(app.state.organizations)):
        if Seq(app.state.organizations[i].get() == Bytes(""),
               app.state.organizations[i].set(organization.get())):
            break

    return Seq(
        Assert(is_owner),
        Approve()
    )


@app.external
def donate(organization: abi.Address, amount: abi.Uint64) -> Expr:
    """
    Handle donations to organizations. Increment global and user-specific donation counters.
    """
    is_valid_organization = Or(
        *[app.state.organizations[i].get() == organization.get() for i in range(len(app.state.organizations))]
    )

    update_user_donation = app.local.user_donations.set(
        app.local.user_donations.get() + amount.get())

    is_valid_donation = Seq(
        Assert(Global.group_size() == 1),
        Assert(Txn.type_enum() == TxnType.Payment),
        Assert(is_valid_organization),
        Assert(Txn.amount() >= amount.get()),
        update_user_donation,
        app.state.donation_counter.set(
            app.state.donation_counter.get() + Int(1)),
        Approve()
    )

    return is_valid_donation


@app.external(read_only=True)
def get_total_donations(*, output: abi.Uint64) -> Expr:
    """
    Retrieve the total number of donations made.
    """
    return output.set(app.state.donation_counter.get())


@app.external(read_only=True)
def get_user_donation(*, output: abi.Uint64) -> Expr:
    """
    Retrieve the total amount donated by the calling user.
    """
    return output.set(app.local.user_donations.get())
