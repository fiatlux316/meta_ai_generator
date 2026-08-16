# Spec 기반으로 Crew AI 프로젝트를 자동으로 생성하기 위한 메타 AI Tool

## 1. uv 설치
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

## 2. crewai 설치 (기존에 설치되어 있으면 생략, 현재는 1.14.x 만 지원)
```bash
uv tool install crewai==1.14.7
```

### 설치 확인
```bash 
uv tool list
```

## 3. python 버전 설정 및 기타 패키지 설치
```bash
uv init --python 3.11. # .python-version, pyproject.toml 자동생성
```

### crewai, pyyaml 패키지 설치
```bash
uv add "crewai[tools]"
uv add pyyaml
```
### 설치 확인
```bash 
uv pip list
```

## 4. crew ai 프로젝트 생성 (./spec_crews/crew_name.csv 참조해서 자동 생성)
```bash
uv run generate.py [crew_name]
```

## 5. 생성된 crew ai 실행 (로컬 환경) : generated_crews/[crew_name] 폴더로 이동

```bash
cd generated_crews/[crew_name]
```

### 기본 패키지 확인
```bash
uv sync  # 해당 폴더에 .venv 자동 생성
# 필요시 로컬 가상환경에 패키지 추가
uv add "crewai[bedrock]"
uv add agentops # 모니터링 AgentOps 사용시
```

### 필요한 Custom Tool 작성 (작성 예)
- src/[CREW_NAME]/tools/custom_tool.py 에  tool 의 실제 로직 작성

```python

# 사전에 작성된 외부 연동 API 및 패키지를 임포트하여 로직 구현
from .datadog_api import datadog_apm_search, datadog_logs_search

class DatadogLogsSearchInput(BaseModel):
    """Input schema for DatadogLogsSearch."""
    limit: str = Field(..., description="limit에 대한 설명을 자세하게 입력하세요.")
    recipient_email: str = Field(..., description="recipient_email에 대한 설명을 자세하게 입력하세요.")
    time_range: str = Field(..., description="time_range에 대한 설명을 자세하게 입력하세요.")
    datadog_query: str = Field(..., description="datadog_query에 대한 설명을 자세하게 입력하세요.")
    
class DatadogLogsSearch(BaseTool):
    name: str = "DatadogLogsSearch"
    description: str = "DatadogLogsSearch에 대한 설명을 자세하게 입력하세요."
    args_schema: Type[BaseModel] = DatadogLogsSearchInput

    def _run(self, limit:str, recipient_email:str, time_range:str, datadog_query:str) -> str:
        
        # [이부분이 핵심] 실제 로직을 처리하는 api 적용
        limit = int(limit)
        return datadog_apm_search(datadog_query, time_range, limit)
```

### Tool import 확인
- src/[CREW_NAME]/crew.py 에 해당 Tool 추가되었는지 확인

```python
from .tools.custom_tool import DatadogLogsSearch
....

    # ── Tool 등록 (YAML에서 이름으로 참조됨) ──
    @agent
    def datadog_log_retrieval_specialist(self) -> Agent:
        return Agent(
            config=self.agents_config['datadog_log_retrieval_specialist'],
            tools=[DatadogLogsSearch()],
            verbose=True,
            reasoning=False,
            max_reasoning_attempts=None,
            inject_date=True,
            allow_delegation=False,
            max_iter=20,
            max_rpm=None,
            max_execution_time=None,
            llm=llm
        )
```

### agentops 설정 (모니터링용, 선택)
- [CREW_NAME]/.env 파일에 AGENTOPS_API_KEY=xxxx 추가
- src/[CREW_NAME]/crew.py 에 아래 내용 추가

```python
from dotenv import load_dotenv
load_dotenv()

import agentops
# 2. AgentOps 초기화 (반드시 CrewAI 컴포넌트 생성 전에 호출)
# tags 인자를 넣으면 대시보드에서 프로젝트를 분류해서 보기 편합니다.
agentops.init(tags=['my_auto_crew'])
```

### crew 실행
```bash
uv run run_crew
```

## 6. crew ai 디플로이 (./generated_crews/[crew_name] 참조)
### 자체 AMP 서버에 배포하여 웹기반에서 실행하기 위함
### AMP_URL, AMP_KEY 를 환경변수에 반드시 세팅 후 실행

```bash
uv run deploy.py [crew_name]
```