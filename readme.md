# Spec 기반으로 Crew AI 를 만들기 위한 메타 AI Tool

# uv 설치
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

# uv init
```bash
uv init
uv venv
```

# crewai 설치 (기존에 설치되어 있으면 생략)
```bash
uv tool install crewai
```

# pyyaml 설치
```bash
uv pip install pyyaml
```

# 설치 확인
```bash 
uv tool list
```

# crew ai 생성
```bash
uv run build.py 
```

# 생성된 crew ai 실행
## 기본 패키지 확인
- 해당 crew 폴더로 이동 (예 : cd generated_crews/my_auto_crew)
- 파이썬 3.11.0 ~ 3.13.x 버전이 필요한데 가상환경에 설치가 안되어 있으면 설치 
  - pyproject.toml 에 requires-python = ">=3.11,<3.14"
  - uv command 가 version 을 확인하지 않기 때문에 직접 설치해야함

```bash
uv tool install python@3.13.3
```

## 필요한 tool 작성
- src/[CREW_NAME]/tools/custom_tool.py

```python
from crewai.tools import tool

@tool
def load_csv(input_file: str) -> str:    
    """CSV 파일을 로드하여 데이터프레임을 csv 형태로 반환합니다."""
    import pandas as pd
    print(f"\n\n\n\n\n{input_file}\n\n\n\n\n")
    df = pd.read_csv(input_file)
    print("\n\n")
    print("CSV 파일 로드 완료")
    print(df.head())
    print(f"\n\n")
    return df.to_csv(index=False)
```

## tool import 설정
- src/[CREW_NAME]/crew.py

```python
    from crewai.tools import tool
    from my_auto_crew.tools.custom_tool import load_csv as _load_csv
    
    # ── Tool 등록 (YAML에서 이름으로 참조됨) ──
    @tool
    def load_csv(self):
        return _load_csv
```

## LLM 설정  (devx api)
- src/[CREW_NAME]/crew.py

```python
from devx_llm_wrapper import llm

# agent 에 llm 설정
@agent
def researcher(self) -> Agent:
    return Agent(
        config=self.agents_config['researcher'], # type: ignore[index]
        verbose=True,
        llm=llm # <--- 에 추가
    )
```

## agentops 설정 (선택)
- src/[CREW_NAME]/crew.py 

```python
from dotenv import load_dotenv
load_dotenv()

import agentops
# 2. AgentOps 초기화 (반드시 CrewAI 컴포넌트 생성 전에 호출)
# tags 인자를 넣으면 대시보드에서 프로젝트를 분류해서 보기 편합니다.
agentops.init(tags=['my_auto_crew'])
```

## 실행
```bash
uv run run_crew
```
