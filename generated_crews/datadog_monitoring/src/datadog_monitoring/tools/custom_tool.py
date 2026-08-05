from crewai.tools import BaseTool
from typing import Type
from pydantic import BaseModel, Field

from datadog_monitoring.tools.datadog_api import datadog_apm_search, datadog_logs_search

class DatadogLogsSearchInput(BaseModel):
    """Input schema for DatadogLogsSearch."""
    recipient_email: str = Field(..., description="recipient_email에 대한 설명을 자세하게 입력하세요.")
    time_range: str = Field(..., description="time_range에 대한 설명을 자세하게 입력하세요.")
    datadog_query: str = Field(..., description="datadog_query에 대한 설명을 자세하게 입력하세요.")
    output_path: str = Field(..., description="output_path에 대한 설명을 자세하게 입력하세요.")
    limit: str = Field(..., description="limit에 대한 설명을 자세하게 입력하세요.")
    

class DatadogLogsSearch(BaseTool):
    name: str = "DatadogLogsSearch"
    description: str = "DatadogLogsSearch에 대한 설명을 자세하게 입력하세요."
    args_schema: Type[BaseModel] = DatadogLogsSearchInput

    def _run(self, recipient_email:str, time_range:str, datadog_query:str, output_path:str, limit:str) -> str:

        # custom logic to process the inputs and call the Datadog API
        limit = int(limit)  # Convert limit to integer
        return datadog_logs_search(datadog_query, time_range, limit)