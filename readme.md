# Spec 기반으로 Crew AI 프로젝트를 자동으로 생성하기 위한 메타 AI Tool

## uv 설치
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

## crewai 설치 (기존에 설치되어 있으면 생략)
```bash
uv tool install crewai==1.14.7
```

## 설치 확인
```bash 
uv tool list
```

## python 버전 설정
```bash
uv init --python 3.11. # .python-version, pyproject.toml 자동생성
```

## crewai, pyyaml 패키지 설치
```bash
uv add "crewai[tools]"
uv add pyyaml
```
## 설치 확인
```bash 
uv pip list
```

## crew ai 프로젝트 생성 (spec.csv 참조해서 자동 생성)
```bash
uv run build.py 
```

## 생성된 crew ai 실행
### 기본 패키지 확인
- 해당 crew 폴더로 이동 (예 : cd generated_crews/my_auto_crew)

```bash
uv sync  # 해당 폴더에 .venv 자동 생성
# 필요시 로컬 가상환경에 패키지 추가
uv add "crewai[bedrock]"
uv add agentops # 모니터링 AgentOps 사용시
```

### 필요한 Custom Tool 작성 (작성 예)
- src/[CREW_NAME]/tools/custom_tool.py 에  tool 의 실제 로직 작성

```python
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
        # [TODO: Pseudo-code] 실제 비즈니스 로직을 여기에 구현하세요.
        # 예: import pandas as pd
        # df = pd.read_csv('data.csv')
        # return df[df['target'] == query].to_string()
        
        return f"[DatadogLogsSearch] 성공적으로 실행되었습니다."
```

### Tool import 확인
- src/[CREW_NAME]/crew.py 에 해당 Tool 추가되었는지 확인

```python
from datadog_log_monitor_reporter.tools.custom_tool import DatadogLogsSearch
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
