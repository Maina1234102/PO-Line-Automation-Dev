import requests
import logging
from backend.app.core.config import settings
from backend.app.schemas.po_models import LineItem
from backend.app.services.mappings import mapping_service

logger = logging.getLogger(__name__)

class OracleService:
    def get_po_header_id(self, order_number: str) -> str:
        url = f"{settings.ORACLE_BASE_URL}/fscmRestApi/resources/latest/purchaseOrders?q=OrderNumber='{order_number}'"
        try:
            response = requests.get(url, auth=(settings.ORACLE_USER, settings.ORACLE_PASS))
            response.raise_for_status()
            data = response.json()
            
            if "items" in data and len(data["items"]) > 0:
                return data["items"][0].get("POHeaderId")
            return None
        except requests.exceptions.RequestException as e:
            logger.error(f"Oracle GET API Error: {e}")
            raise

    def create_line_item(self, po_header_id: str, line_item: LineItem) -> tuple[bool, str]:
        url = f"{settings.ORACLE_BASE_URL}/fscmRestApi/resources/11.13.18.05/draftPurchaseOrders/{po_header_id}/child/lines"
        
        # Pre-process logic (mapping lookups)
        # Note: We are modifying the Pydantic model in place or before dumping
        
        if line_item.schedules:
            for schedule in line_item.schedules:
                if schedule.distributions:
                    for dist in schedule.distributions:
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

                                # 3. Organization Name Lookup
                                raw_org = str(proj.organization_id) if proj.organization_id is not None else ""
                                mapped_org = mapping_service.get_organization_id(raw_org)

                                if mapped_org:
                                    logger.info(f"Mapping Organization Name '{raw_org}' to ID '{mapped_org}'")
                                    proj.organization_id = mapped_org
                                else:
                                    if raw_org and not raw_org.isdigit():
                                         error_msg = f"Organization ID not found for name: {raw_org}"
                                         logger.error(error_msg)
                                         return False, error_msg

        # Dump using aliases to match Oracle expected JSON format
        payload = line_item.model_dump(by_alias=True, exclude_none=True)

        headers = {
            "Content-Type": "application/json"
        }

        try:
            logger.info(f"Creating line item with payload: {payload}")
            response = requests.post(url, auth=(settings.ORACLE_USER, settings.ORACLE_PASS), json=payload, headers=headers)
            
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

oracle_service = OracleService()
