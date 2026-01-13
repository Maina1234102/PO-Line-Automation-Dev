import pandas as pd
import os
import logging
from backend.app.core.config import settings

logger = logging.getLogger(__name__)

class MappingService:
    def __init__(self):
        self.project_mapping = {}
        self.expenditure_mapping = {}
        self.organization_mapping = {}
        
        # Determine the directory where mapping files are located
        # Assuming they are in the 'backend' root folder
        self.backend_dir = settings.BACKEND_DIR

    def load_mappings(self):
        self.load_project_mapping()
        self.load_expenditure_mapping()
        self.load_organization_mapping()

    def load_project_mapping(self):
        mapping_file = os.path.join(self.backend_dir, "project_mapping.xlsx")
        try:
            if os.path.exists(mapping_file):
                df = pd.read_excel(mapping_file)
                self.project_mapping = dict(zip(df["ProjectNumber"].astype(str), df["ProjectId"].astype(str)))
                logger.info(f"Loaded {len(self.project_mapping)} project mappings.")
            else:
                logger.warning(f"Mapping file {mapping_file} not found.")
        except Exception as e:
            logger.error(f"Failed to load project mapping: {e}")

    def load_expenditure_mapping(self):
        mapping_file = os.path.join(self.backend_dir, "expenditure_mapping.xlsx")
        try:
            if os.path.exists(mapping_file):
                df = pd.read_excel(mapping_file)
                self.expenditure_mapping = dict(zip(df["ExpenditureTypeName"].astype(str), df["ExpenditureTypeId"].astype(str)))
                logger.info(f"Loaded {len(self.expenditure_mapping)} expenditure mappings.")
            else:
                logger.warning(f"Mapping file {mapping_file} not found.")
        except Exception as e:
            logger.error(f"Failed to load expenditure mapping: {e}")

    def load_organization_mapping(self):
        mapping_file = os.path.join(self.backend_dir, "organization_mapping.xlsx")
        try:
            if os.path.exists(mapping_file):
                df = pd.read_excel(mapping_file)
                self.organization_mapping = dict(zip(df["OrganizationName"].astype(str), df["OrganizationId"].astype(str)))
                logger.info(f"Loaded {len(self.organization_mapping)} organization mappings.")
            else:
                logger.warning(f"Mapping file {mapping_file} not found.")
        except Exception as e:
            logger.error(f"Failed to load organization mapping: {e}")

    def get_project_id(self, project_number: str) -> str:
        return self.project_mapping.get(project_number)

    def get_expenditure_type_id(self, expenditure_type: str) -> str:
        return self.expenditure_mapping.get(expenditure_type)

    def get_organization_id(self, organization_name: str) -> str:
        return self.organization_mapping.get(organization_name)

# Singleton instance
mapping_service = MappingService()
