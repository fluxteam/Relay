from typing import Any, Dict, Optional, Union
from pyconduit import Category, Job
from pyconduit import block
import httpx
from relay.enums import RelayFlags
from relay.utils import load_json, parse_run
from relay.commons import BASE_URL, sio
from hikari import Guild

class Miscellaneous(Category):
    """
    Additional blocks to increase Relay's capabilities.
    """

    @block()
    @staticmethod
    async def http_request(
        guild__ : Guild,
        *,
        url : str,
        method : str = "GET",
        headers : Dict[str, Any] = None,
        data : Optional[Dict[str, Any]] = None,
        params : Optional[Dict[str, Any]] = None
    ) -> httpx.Response:
        """
        Makes a HTTP request to a specific URL.

        !!! warning "This block has some limitations"
            * Relay will set HTTP timeout to 3 seconds. The server must respond in 3 seconds.
            * All requests will have a custom user agent set by Relay.
            * `data` parameter only accepts a dictionary (JSON) for now.

        Args:
            url:
                URL of the request.
            method:
                Method of the request. (default: GET)
            headers:
                Headers of the request. (default: None)
            data:
                A dictionary that will be sent as body JSON (default: None)
            params:
                A dictionary of query parameters. (default: None)

        Returns:
            A Response object.
        """
        h = {} if not headers else headers.copy()
        h["user-agent"] = f"Mozilla/5.0 (compatible; Relay/0.1; +{BASE_URL})"
        async with httpx.AsyncClient(
            trust_env = False, 
            max_redirects = 3,
            follow_redirects = True
        ) as client:
            response = await client.request(
                method, 
                url, 
                params = params, 
                headers = h, 
                json = data,
                timeout = 3
            )
            return response


    @block()
    @staticmethod
    async def http_status(
        *,
        response : httpx.Response
    ) -> int:
        """
        Gets the status code from a Response.

        Args:
            response:
                A HTTP response object.
        
        Returns:
            An integer.
        """
        return response.status_code

    
    @block()
    @staticmethod
    async def http_headers(
        *,
        response : httpx.Response
    ) -> Dict[str, Any]:
        """
        Gets the headers from response.

        Args:
            response:
                A HTTP response object.
        
        Returns:
            A headers dictionary.
        """
        return dict(response.headers)

    
    @block()
    @staticmethod
    async def http_content(
        *,
        response : httpx.Response
    ) -> Union[Dict, str]:
        """
        Gets the content from response.

        Args:
            response:
                A HTTP response object.
        
        Returns:
            The returned response of request. If response is a valid JSON, then it will be automatically
            parsed as dictionary. But if not, then you will get the response as UTF-8 string.
        """
        content = await response.aread()
        return load_json(content, content if content else content.decode("utf-8"))


    @block
    @staticmethod
    async def display_log(
        guild__ : Guild,
        job__ : Job,
        *,
        content : Optional[Any] = None
    ) -> None:
        """
        Displays a text in log window.

        Args:
            content:
                The content that will be displayed in log.
        """
        t, c, e, w = parse_run(job__.id)
        await sio.emit("relay_actions_log", {
            "server": str(guild__.id), 
            "workflow": w,
            "event": e,
            "log": "" if content == None else str(content),
            "log_type": "INFO"
        }, namespace = "/admin")

