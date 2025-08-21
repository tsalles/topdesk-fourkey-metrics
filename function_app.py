import azure.functions as func
import fastapi
import requests
from typing import List, Optional, Dict, Any
from dotenv import load_dotenv
import os
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
import secrets
from loguru import logger 

load_dotenv()

class TopDeskClient:
    """
    Python client for the TopDesk Metrics API (4Key) using Basic Auth.
    """

    def __init__(self, base_url: str, username: str, password: str):
        """
        :param base_url: Base URL of the TopDesk API, e.g., "https://cartaoelo.topdesk.net/tas/api"
        :param username: API username
        :param password: API password
        """
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()
        self.session.auth = (username, password)
        self.session.headers.update({
            "Accept": "application/json"
        })

    # ------------------------------
    # Incident Endpoints
    # ------------------------------
    def list_incidents(self, pageStart: Optional[int] = None,
                             pageSize: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Listar chamados (incidentes).
        """
        logger.info(f"Fetching incidents with pageStart: {pageStart}, pageSize: {pageSize}")
        url = f"{self.base_url}/incidents"
        params = {}
        if pageStart is not None or pageSize is not None:
            if pageStart is not None:
                params["pageStart"] = pageStart
            if pageSize is not None:
                params["pageSize"] = pageSize
        resp = self.session.get(url, params=params)
        resp.raise_for_status()
        return resp.json()
    
    def get_incident_by_id(self, incident_id: str) -> Dict[str, Any]:
        url = f"{self.base_url}/incidents/id/{incident_id}"
        resp = self.session.get(url)
        resp.raise_for_status()
        return resp.json()
    
    # ------------------------------
    # Transaction Assets
    # ------------------------------
    def get_transaction_assets(
        self,
        template_id: Optional[str] = None,
        fields: Optional[List[str]] = None,
        filter: Optional[str] = None,
        pageStart: Optional[int] = None,
        pageSize: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Obter dados transacionais (por TemplateID).

        :param template_id: Template ID (string)
        :param fields: Optional list of fields to include
        """
        logger.info(f"Fetching assets for template_id: {template_id}, fields: {fields}, filter: {filter}, pageStart: {pageStart}, pageSize: {pageSize}")
        url = f"{self.base_url}/assetmgmt/assets"
        params = {}
        if template_id:
            params["templateId"] = template_id
        if fields:
            params["field"] = fields
        if filter:
            params["$filter"] = filter
        if pageStart is not None or pageSize is not None:
            if pageStart is not None:
                params["pageStart"] = pageStart
            if pageSize is not None:
                params["pageSize"] = pageSize
        resp = self.session.get(url, params=params)
        resp.raise_for_status()
        return resp.json().get('dataSet', [])
    
    def get_asset_by_id(self, asset_id: str) -> Dict[str, Any]:
        url = f"{self.base_url}/assetmgmt/assets/id/{asset_id}"
        resp = self.session.get(url)
        resp.raise_for_status()
        return resp.json()

    # ------------------------------
    # Change Records
    # ------------------------------
    def list_changes(self, fields: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Listar mudanças (Change records).

        :param fields: Optional, e.g. "all"
        """
        url = f"{self.base_url}/operatorChanges"
        params = {}
        if fields:
            params["fields"] = fields
        resp = self.session.get(url, params=params)
        resp.raise_for_status()
        return resp.json().get('results', [])
    
    def get_change_by_id(self, change_id: str, fields: Optional[str] = None) -> Dict[str, Any]:
        url = f"{self.base_url}/operatorChanges/{change_id}"
        params = {}
        if fields:
            params["fields"] = fields
        resp = self.session.get(url, params=params)
        resp.raise_for_status()
        return resp.json()


fapi_app = fastapi.FastAPI(
    title="FourKey Metrics - TopDesk API",
    description="API para consultar incidentes, ativos e mudanças no TopDesk.",
    version="1.0.0",
    contact={
        "name": "Thiago Salles",
        "email": "thiagosalles@microsoft.com",
    },
    license_info={
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT",
    },
    openapi_tags=[
        {
            "name": "Incident",
            "description": "Endpoints relacionados a incidentes no TopDesk.",
        },
        {
            "name": "Assets",
            "description": "Endpoints relacionados a ativos transacionais no TopDesk.",
        },
        {
            "name": "Changes",
            "description": "Endpoints relacionados a mudanças (Change records) no TopDesk.",
        }
    ],
    openapi_version="3.0.1"
)


def get_topdesk_client():
    base_url = "https://cartaoelo.topdesk.net/tas/api"
    user = os.getenv("TOPDESK_USER", "aaa")
    password = os.getenv("TOPDESK_API_KEY", "aaa")
    if not user or not password:
        raise RuntimeError("TOPDESK_USER or TOPDESK_API_KEY not set in .env file.")
    return TopDeskClient(base_url=base_url, username=user, password=password)

security = HTTPBasic()
API_USERNAME = os.getenv("API_USERNAME", "apiuser")
API_PASSWORD = os.getenv("API_PASSWORD", "apipass")

def verify_basic_auth(credentials: HTTPBasicCredentials = Depends(security)):
    # Replace with your desired username/password
    correct_username = secrets.compare_digest(credentials.username, API_USERNAME)
    correct_password = secrets.compare_digest(credentials.password, API_PASSWORD)
    if not (correct_username and correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username


@fapi_app.get(
    "/v1/incidents",
    operation_id="list_incidents",
    response_model=List[Dict[str, Any]],
    tags=["Incident"],
    summary="Retorna incidentes do TopDesk",
    description="Lista todos os incidentes."
)
def list_incidents(
    pageStart: Optional[int] = None, pageSize: Optional[int] = None, _: str = Depends(verify_basic_auth)
) -> List[Dict[str, Any]]:
    logger.info('GET /v1/incidents')
    client = get_topdesk_client()
    try:
        # Pass pagination params to TopDeskClient when implemented
        return client.list_incidents(pageStart, pageSize)  # TODO: add pagination support in client
    except Exception as e:
        logger.error(str(e))
        return []

@fapi_app.get(
    "/v1/incidents/{incident_id:str}",
    operation_id="get_incident",
    response_model=Dict[str, Any],
    tags=["Incident"],
    summary="Retorna incidente específico do TopDesk dado seu identificador.",
    description="Obtém um incidente específico pelo ID."
)
def get_incident(incident_id: str, _: str = Depends(verify_basic_auth)) -> Dict[str, Any]:
    logger.info('GET /v1/incidents')
    client = get_topdesk_client()
    try:
        return client.get_incident_by_id(incident_id)
    except Exception as e:
        logger.error(str(e))
        return {}

@fapi_app.get(
    "/v1/assets",
    operation_id="list_assets",
    response_model=List[Dict[str, Any]],
    tags=["Assets"],
    summary="Retorna ativos do TopDesk",
    description="Lista todos os ativos transacionais por Template ID."
)
def list_assets(
    template_id: Optional[str] = None,
    fields: Optional[str] = None,
    filter: Optional[str] = None,
    pageStart: Optional[int] = None,
    pageSize: Optional[int] = None,
    _: str = Depends(verify_basic_auth)
) -> List[Dict[str, Any]]:
    logger.info('GET /v1/assets')
    client = get_topdesk_client()    
    fields_lst = None
    if fields:
        fields = fields.strip()
        if fields:
            fields_lst = fields.split(',')
    try:
        return client.get_transaction_assets(template_id=template_id,
                                             fields=fields_lst, filter=filter,
                                             pageStart=pageStart, pageSize=pageSize)
    except Exception as e:
        logger.error(str(e))
        return [] # fixme: fastapi must return server side error with error message

@fapi_app.get(
    "/v1/assets/{asset_id:str}",
    operation_id="get_asset",
    response_model=Dict[str, Any],
    tags=["Assets"],
    summary="Retorna ativo do TopDesk dado seu identificador.",
    description="Obtém um ativo específico pelo ID."
)
def get_asset(asset_id: str, user: str = Depends(verify_basic_auth)) -> Dict[str, Any]:
    logger.info('GET /assets')
    client = get_topdesk_client()
    try:
        return client.get_asset_by_id(asset_id)
    except Exception as e:
        logger.error(str(e))
        return {} # fixme: fastapi must return server side error with error message
    

@fapi_app.get(
    "/v1/changes",
    operation_id="list_changes",
    response_model=List[Dict[str, Any]],
    tags=["Changes"],
    summary="Retorna mudanças (changes) do TopDesk.",
    description="Lista todas as mudanças."
)
def list_changes(fields: Optional[str], user: str = Depends(verify_basic_auth)) -> List[Dict[str, Any]]:
    logger.info('GET /changes')
    client = get_topdesk_client()
    try:
        return client.list_changes(fields=fields)
    except Exception as e:
        logger.error(str(e))
        return [] # fix me: fastapi must return server side error with error message
    
@fapi_app.get(
    "/v1/changes/{change_id:str}",
    operation_id="get_change",
    response_model=Dict[str, Any],
    tags=["Changes"],
    summary="Retorna uma mudança específica do TopDesk dado seu identificador.",
    description="Obtém uma mudança específica pelo ID."
)
def get_change(change_id: str, fields: Optional[str], user: str = Depends(verify_basic_auth)) -> Dict[str, Any]:
    logger.info('GET /changes/{change_id}')
    client = get_topdesk_client()
    try:
        return client.get_change_by_id(change_id, fields)
    except Exception as e:
        logger.error(str(e))
        return {} # fix me: fastapi must return server side error with error message
    

app = func.AsgiFunctionApp(app=fapi_app, http_auth_level=func.AuthLevel.ANONYMOUS)
