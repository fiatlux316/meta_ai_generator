# Spec 기반으로 Crew AI 를 만들기 위한 메타 AI Tool

# uv 설치
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

# crewai 설치 (기존에 설치되어 있으면 생략)
```bash
uv tool install crewai
```

# 설치 확인
```bash 
uv tool list
```

# python 3.11 설정
```bash
uv init --python 3.11. # .python-version, pyproject.toml 자동생성
```

# crewai, pyyaml 설치
```bash
uv add "crewai[tools]"
uv add pyyaml
```
# 설치 확인
```bash 
uv pip list
```

# crew ai 생성
```bash
uv run build.py 
```

# 생성된 crew ai 실행
## 기본 패키지 확인
- 해당 crew 폴더로 이동 (예 : cd generated_crews/my_auto_crew)

```bash
uv sync  # 해당 폴더에 .venv 자동 생성
# 필요시 로컬 가상환경에 패키지 추가
uv add agentops # 모니터링 AgentOps 사용시
```

## 필요한 tool 작성
- src/[CREW_NAME]/tools/custom_tool.py 에 필요한 tool 작성

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
- src/[CREW_NAME]/crew.py 에 아래 내용 추가

```python
    from crewai.tools import tool
    from my_auto_crew.tools.custom_tool import load_csv as _load_csv
    
    # ── Tool 등록 (YAML에서 이름으로 참조됨) ──
    @tool
    def load_csv(self):
        return _load_csv
```

## agentops 설정 (선택)
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

## 실행
```bash
uv run run_crew
```
