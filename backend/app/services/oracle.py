import requests
import logging
from backend.app.core.config import settings
from backend.app.schemas.po_models import LineItem
from backend.app.services.mappings import mapping_service

logger = logging.getLogger(__name__)

class OracleService:
    def get_po_header_id(self, order_number: str, auth: tuple = None) -> str:
        url = f"{settings.ORACLE_BASE_URL}/fscmRestApi/resources/latest/purchaseOrders?q=OrderNumber='{order_number}'"
        try:
            # Use provided auth or fallback to settings (fallback for migration/test)
            request_auth = auth if auth else (settings.ORACLE_USER, settings.ORACLE_PASS)
            response = requests.get(url, auth=request_auth)
            response.raise_for_status()
            data = response.json()
            
            if "items" in data and len(data["items"]) > 0:
                return data["items"][0].get("POHeaderId")
            return None
        except requests.exceptions.RequestException as e:
            logger.error(f"Oracle GET API Error: {e}")
            raise

    def create_line_item(self, po_header_id: str, line_item: LineItem, auth: tuple = None) -> tuple[bool, str]:
        url = f"{settings.ORACLE_BASE_URL}/fscmRestApi/resources/11.13.18.05/draftPurchaseOrders/{po_header_id}/child/lines"
        
        # Pre-process logic (mapping lookups)
        # Note: We are modifying the Pydantic model in place or before dumping
        
        if line_item.schedules:
            for schedule in line_item.schedules:
                # If DestinationType is Inventory, we must not pass POChargeAccount
                is_inventory = schedule.destination_type and schedule.destination_type.lower() == "inventory"
                
                if schedule.distributions:
                    for dist in schedule.distributions:
                        if is_inventory:
                            logger.info(f"DestinationType is 'Inventory' for line {line_item.line_number}. Stripping POChargeAccount.")
                            dist.po_charge_account = None

                        if dist.project_dff:
                            for proj in dist.project_dff:
                                # 1. Project Number Lookup
                                raw_id = str(proj.project_id) if proj.project_id is not None else ""
                                mapped_id = mapping_service.get_project_id(raw_id)
                                
                                if mapped_id:
                                    logger.info(f"Mapping Project Number '{raw_id}' to ID '{mapped_id}'")
                                    proj.project_id = mapped_id
                                elif raw_id and len(raw_id) < 15:
                                    error_msg = f"Project ID not found for: {raw_id}"
                                    logger.error(error_msg)
                                    return False, error_msg

                                # 2. Expenditure Name Lookup
                                raw_exp = str(proj.expenditure_type_id) if proj.expenditure_type_id is not None else ""
                                mapped_exp = mapping_service.get_expenditure_type_id(raw_exp)
                                
                                if mapped_exp:
                                     logger.info(f"Mapping Expenditure Name '{raw_exp}' to ID '{mapped_exp}'")
                                     proj.expenditure_type_id = mapped_exp
                                else:
                                     if raw_exp and not raw_exp.isdigit():
                                          error_msg = f"Expenditure Type ID not found for name: {raw_exp}"
                                          logger.error(error_msg)
                                          # return False, error_msg # Kept consistent with legacy

                                # No mapping needed for Organization Name as it is now passed as Display Name
                                pass

        # Dump using aliases to match Oracle expected JSON format
        payload = line_item.model_dump(by_alias=True, exclude_none=True)

        headers = {
            "Content-Type": "application/json"
        }

        try:
            logger.info(f"Creating line item with payload: {payload}")
            request_auth = auth if auth else (settings.ORACLE_USER, settings.ORACLE_PASS)
            response = requests.post(url, auth=request_auth, json=payload, headers=headers)
            
            if response.status_code in [200, 201]:
                logger.info(f"Line item {line_item.line_number} created successfully.")
                return True, None
            else:
                error_details = response.text
                logger.error(f"Oracle POST API Failed for line {line_item.line_number}: {response.status_code} - {error_details}")
                return False, f"{response.status_code} - {error_details}"
        except requests.exceptions.RequestException as e:
            logger.error(f"Oracle POST API Error: {e}")
            return False, str(e)

    def verify_credentials(self, auth: tuple) -> bool:
        """Verifies Oracle credentials by making a simple metadata call."""
        url = f"{settings.ORACLE_BASE_URL}/fscmRestApi/resources/latest/purchaseOrders?limit=1"
        try:
            response = requests.get(url, auth=auth)
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Credential verification failed: {e}")
            return False

oracle_service = OracleService()
