"""Schemas for the accounts tool group: get_account."""

from pydantic import BaseModel, ConfigDict

from ._base import ToolResult


class AccountAddressData(BaseModel):
    model_config = ConfigDict(extra="allow")

    city: str | None = None
    country: str | None = None
    street: str | None = None
    zipCode: str | None = None


class AccountPlanItemData(BaseModel):
    model_config = ConfigDict(extra="allow")

    credits: float | None = None
    creditsType: str | None = None
    endDate: str | None = None
    startDate: str | None = None
    type: str | None = None


class AccountRelayDataData(BaseModel):
    model_config = ConfigDict(extra="allow")

    port: int | None = None
    relay: str | None = None
    userName: str | None = None


class AccountRelayData(BaseModel):
    model_config = ConfigDict(extra="allow")

    data: AccountRelayDataData | None = None
    enabled: bool | None = None


class AccountMarketingAutomationData(BaseModel):
    model_config = ConfigDict(extra="allow")

    enabled: bool | None = None
    key: str | None = None


class GetAccountData(BaseModel):
    model_config = ConfigDict(extra="allow")

    organization_id: str | None = None
    user_id: int | None = None
    enterprise: bool | None = None
    companyName: str | None = None
    email: str | None = None
    firstName: str | None = None
    lastName: str | None = None
    address: AccountAddressData | None = None
    marketingAutomation: AccountMarketingAutomationData | None = None
    plan: list[AccountPlanItemData] | None = None
    relay: AccountRelayData | None = None


class GetAccountResult(ToolResult):
    data: GetAccountData | None = None
