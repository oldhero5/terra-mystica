"""
HTTP Tools for MCP Server
Provides HTTP client functionality for FastAPI endpoint interactions
"""

import asyncio
from typing import Dict, Any, Optional, Union
import httpx
import json
import structlog
from urllib.parse import urljoin

logger = structlog.get_logger(__name__)


class HTTPTools:
    """HTTP client tools for MCP server"""
    
    def __init__(self, base_url: str = "http://localhost:8000", timeout: float = 30.0):
        """
        Initialize HTTP tools
        
        Args:
            base_url: Base URL for API requests
            timeout: Request timeout in seconds
        """
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.client = None
        logger.info("HTTPTools initialized", base_url=self.base_url, timeout=timeout)
    
    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create HTTP client"""
        if self.client is None:
            self.client = httpx.AsyncClient(
                timeout=self.timeout,
                headers={
                    "User-Agent": "Terra-Mystica-MCP-Client/1.0.0",
                    "Content-Type": "application/json",
                }
            )
        return self.client
    
    def _build_url(self, endpoint: str) -> str:
        """Build full URL from endpoint"""
        if endpoint.startswith('http'):
            return endpoint
        return urljoin(self.base_url + '/', endpoint.lstrip('/'))
    
    def _prepare_headers(self, headers: Optional[Dict[str, str]] = None) -> Dict[str, str]:
        """Prepare request headers"""
        default_headers = {
            "User-Agent": "Terra-Mystica-MCP-Client/1.0.0",
            "Accept": "application/json",
        }
        if headers:
            default_headers.update(headers)
        return default_headers
    
    async def get(self, endpoint: str, 
                  params: Optional[Dict[str, Any]] = None,
                  headers: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """
        Make HTTP GET request
        
        Args:
            endpoint: API endpoint (relative to base URL)
            params: Query parameters
            headers: Request headers
            
        Returns:
            Response data as dictionary
        """
        try:
            client = await self._get_client()
            url = self._build_url(endpoint)
            request_headers = self._prepare_headers(headers)
            
            logger.info("Making GET request", url=url, params=params)
            
            response = await client.get(
                url,
                params=params,
                headers=request_headers
            )
            
            result = await self._process_response(response, "GET", url)
            return result
            
        except Exception as e:
            logger.error("GET request failed", endpoint=endpoint, error=str(e))
            return {
                "error": str(e),
                "endpoint": endpoint,
                "method": "GET"
            }
    
    async def post(self, endpoint: str,
                   data: Optional[Dict[str, Any]] = None,
                   json: Optional[Dict[str, Any]] = None,
                   headers: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """
        Make HTTP POST request
        
        Args:
            endpoint: API endpoint (relative to base URL)
            data: Form data
            json: JSON data
            headers: Request headers
            
        Returns:
            Response data as dictionary
        """
        try:
            client = await self._get_client()
            url = self._build_url(endpoint)
            request_headers = self._prepare_headers(headers)
            
            logger.info("Making POST request", url=url, has_data=data is not None, has_json=json is not None)
            
            response = await client.post(
                url,
                data=data,
                json=json,
                headers=request_headers
            )
            
            result = await self._process_response(response, "POST", url)
            return result
            
        except Exception as e:
            logger.error("POST request failed", endpoint=endpoint, error=str(e))
            return {
                "error": str(e),
                "endpoint": endpoint,
                "method": "POST"
            }
    
    async def put(self, endpoint: str,
                  data: Optional[Dict[str, Any]] = None,
                  json: Optional[Dict[str, Any]] = None,
                  headers: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """
        Make HTTP PUT request
        
        Args:
            endpoint: API endpoint (relative to base URL)
            data: Form data
            json: JSON data
            headers: Request headers
            
        Returns:
            Response data as dictionary
        """
        try:
            client = await self._get_client()
            url = self._build_url(endpoint)
            request_headers = self._prepare_headers(headers)
            
            logger.info("Making PUT request", url=url, has_data=data is not None, has_json=json is not None)
            
            response = await client.put(
                url,
                data=data,
                json=json,
                headers=request_headers
            )
            
            result = await self._process_response(response, "PUT", url)
            return result
            
        except Exception as e:
            logger.error("PUT request failed", endpoint=endpoint, error=str(e))
            return {
                "error": str(e),
                "endpoint": endpoint,
                "method": "PUT"
            }
    
    async def delete(self, endpoint: str,
                     params: Optional[Dict[str, Any]] = None,
                     headers: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """
        Make HTTP DELETE request
        
        Args:
            endpoint: API endpoint (relative to base URL)
            params: Query parameters
            headers: Request headers
            
        Returns:
            Response data as dictionary
        """
        try:
            client = await self._get_client()
            url = self._build_url(endpoint)
            request_headers = self._prepare_headers(headers)
            
            logger.info("Making DELETE request", url=url, params=params)
            
            response = await client.delete(
                url,
                params=params,
                headers=request_headers
            )
            
            result = await self._process_response(response, "DELETE", url)
            return result
            
        except Exception as e:
            logger.error("DELETE request failed", endpoint=endpoint, error=str(e))
            return {
                "error": str(e),
                "endpoint": endpoint,
                "method": "DELETE"
            }
    
    async def patch(self, endpoint: str,
                    data: Optional[Dict[str, Any]] = None,
                    json: Optional[Dict[str, Any]] = None,
                    headers: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """
        Make HTTP PATCH request
        
        Args:
            endpoint: API endpoint (relative to base URL)
            data: Form data
            json: JSON data
            headers: Request headers
            
        Returns:
            Response data as dictionary
        """
        try:
            client = await self._get_client()
            url = self._build_url(endpoint)
            request_headers = self._prepare_headers(headers)
            
            logger.info("Making PATCH request", url=url, has_data=data is not None, has_json=json is not None)
            
            response = await client.patch(
                url,
                data=data,
                json=json,
                headers=request_headers
            )
            
            result = await self._process_response(response, "PATCH", url)
            return result
            
        except Exception as e:
            logger.error("PATCH request failed", endpoint=endpoint, error=str(e))
            return {
                "error": str(e),
                "endpoint": endpoint,
                "method": "PATCH"
            }
    
    async def _process_response(self, response: httpx.Response, method: str, url: str) -> Dict[str, Any]:
        """Process HTTP response"""
        try:
            # Get response info
            status_code = response.status_code
            headers = dict(response.headers)
            
            # Try to parse JSON response
            try:
                if response.headers.get('content-type', '').startswith('application/json'):
                    data = response.json()
                else:
                    data = response.text
            except Exception:
                data = response.text
            
            result = {
                "status_code": status_code,
                "headers": headers,
                "data": data,
                "success": 200 <= status_code < 300,
                "method": method,
                "url": url
            }
            
            # Log response
            if result["success"]:
                logger.info("Request successful", 
                           method=method, url=url, status_code=status_code)
            else:
                logger.warning("Request failed", 
                              method=method, url=url, status_code=status_code, data=data)
            
            return result
            
        except Exception as e:
            logger.error("Response processing failed", method=method, url=url, error=str(e))
            return {
                "error": f"Response processing failed: {str(e)}",
                "status_code": getattr(response, 'status_code', None),
                "method": method,
                "url": url,
                "success": False
            }
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Check API health
        
        Returns:
            Health check response
        """
        return await self.get("/health")
    
    async def check_auth(self, token: str) -> Dict[str, Any]:
        """
        Check authentication token
        
        Args:
            token: Authentication token
            
        Returns:
            Authentication check response
        """
        headers = {"Authorization": f"Bearer {token}"}
        return await self.get("/api/v1/auth/me", headers=headers)
    
    async def upload_file(self, endpoint: str, file_path: str, 
                         field_name: str = "file",
                         additional_data: Optional[Dict[str, Any]] = None,
                         headers: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """
        Upload file to endpoint
        
        Args:
            endpoint: API endpoint for file upload
            file_path: Path to file to upload
            field_name: Form field name for file
            additional_data: Additional form data
            headers: Request headers
            
        Returns:
            Upload response
        """
        try:
            client = await self._get_client()
            url = self._build_url(endpoint)
            request_headers = self._prepare_headers(headers)
            
            # Remove content-type header to let httpx set it for multipart
            if "Content-Type" in request_headers:
                del request_headers["Content-Type"]
            
            logger.info("Uploading file", url=url, file_path=file_path)
            
            # Prepare files and data
            files = {field_name: open(file_path, 'rb')}
            data = additional_data or {}
            
            try:
                response = await client.post(
                    url,
                    files=files,
                    data=data,
                    headers=request_headers
                )
                
                result = await self._process_response(response, "POST", url)
                return result
                
            finally:
                # Close file
                files[field_name].close()
            
        except Exception as e:
            logger.error("File upload failed", endpoint=endpoint, file_path=file_path, error=str(e))
            return {
                "error": str(e),
                "endpoint": endpoint,
                "method": "POST",
                "file_path": file_path
            }
    
    async def close(self):
        """Close HTTP client"""
        if self.client:
            await self.client.aclose()
            self.client = None
            logger.info("HTTP client closed")
    
    async def __aenter__(self):
        """Async context manager entry"""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.close()