from pydantic import BaseModel, Field, validator
from typing import List, Optional, Any

class ProjectDFF(BaseModel):
    project_id: Optional[Any] = Field(None, alias="_PROJECT_ID")
    expenditure_item_date: Optional[str] = Field(None, alias="_EXPENDITURE_ITEM_DATE")
    expenditure_type_id: Optional[Any] = Field(None, alias="_EXPENDITURE_TYPE_ID")
    organization_id: Optional[Any] = Field(None, alias="_ORGANIZATION_ID")
    task_id: Optional[Any] = Field(None, alias="_TASK_ID")
    # contract_id: Optional[Any] = Field(None, alias="_CONTRACT_ID")

    class Config:
        populate_by_name = True

class Distribution(BaseModel):
    distribution_number: Optional[int] = Field(1, alias="DistributionNumber")
    deliver_to_location: Optional[str] = Field("IEIPL MUMBAI WH", alias="DeliverToLocation")
    quantity: Optional[float] = Field(2, alias="Quantity")
    po_charge_account: Optional[str] = Field("1001-41110102-9999-9999-1090-9999-9999-9999", alias="POChargeAccount")
    requester: Optional[str] = Field(None, alias="Requester")
    project_dff: Optional[List[ProjectDFF]] = Field(None, alias="projectDFF")

    class Config:
        populate_by_name = True

    @validator('requester', pre=True)
    def empty_str_to_none(cls, v):
        if v == "":
            return None
        return v

class Schedule(BaseModel):
    schedule_number: Optional[int] = Field(1, alias="ScheduleNumber")
    product_type: Optional[str] = Field("Goods", alias="ProductType")
    quantity: Optional[float] = Field(None, alias="Quantity")
    ship_to_organization: Optional[str] = Field("MUMBAI", alias="ShipToOrganization")
    ship_to_location: Optional[str] = Field("IEIPL MUMBAI WH", alias="ShipToLocation")
    destination_type: Optional[str] = Field("EXPENSE", alias="DestinationType")
    # destination_type_code: Optional[str] = Field("EXPENSE", alias="DestinationTypeCode")
    invoice_match_option: Optional[str] = Field(None, alias="InvoiceMatchOption")
    invoice_match_option_code: Optional[str] = Field("P", alias="InvoiceMatchOptionCode")
    match_approval_level: Optional[str] = Field("2 Way", alias="MatchApprovalLevel")
    receipt_required_flag: Optional[bool] = Field(False, alias="ReceiptRequiredFlag")
    inspection_required_flag: Optional[bool] = Field(True, alias="InspectionRequiredFlag")
    receipt_routing_id: Optional[int] = Field(1, alias="ReceiptRoutingId")
    receipt_close_tolerance_percent: Optional[float] = Field(0, alias="ReceiptCloseTolerancePercent")
    invoice_close_tolerance_percent: Optional[float] = Field(0, alias="InvoiceCloseTolerancePercent")
    requested_delivery_date: Optional[str] = Field(None, alias="RequestedDeliveryDate")
    distributions: List[Distribution] = []

    class Config:
        populate_by_name = True

class LineItem(BaseModel):
    line_number: Optional[Any] = Field(None, alias="LineNumber")
    line_type: Optional[str] = Field("Goods", alias="LineType")
    description: Optional[str] = Field(None, alias="Description")
    category_code: Optional[str] = Field(None, alias="CategoryCode")
    uom: Optional[str] = Field(None, alias="UOM")
    uom_code: Optional[str] = Field(None, alias="UOMCode")
    quantity: Optional[float] = Field(None, alias="Quantity")
    price: Optional[float] = Field(None, alias="Price")
    category: Optional[str] = Field(None, alias="Category")
    item: Optional[str] = Field(None, alias="Item")
    negotiated_flag: Optional[Any] = Field(None, alias="NegotiatedFlag")
    schedules: List[Schedule] = []

    class Config:
        populate_by_name = True

class POSubmission(BaseModel):
    po_number: str = Field(..., alias="poNumber")
    lines: List[LineItem]

    class Config:
        populate_by_name = True
