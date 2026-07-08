import os
import csv
import subprocess
import yaml
from pathlib import Path

def run_scaffolding(crew_name):
    """CrewAI CLI를 사용하여 기본 프로젝트 스캐폴딩을 생성합니다."""
    print(f"\n[Scaffolding] '{crew_name}' 크루 생성을 시작합니다...")
    try:
        # crewai create crew 명령어 실행 (기존 폴더가 없을 경우에만)
        if not os.path.exists(crew_name):
            subprocess.run(["crewai", "create", "crew", crew_name], check=True)
            print(f"[Success] '{crew_name}' 스캐폴딩 완료.")
        else:
            print(f"[Skip] '{crew_name}' 폴더가 이미 존재합니다.")
    except subprocess.CalledProcessError as e:
        print(f"[Error] CLI 실행 중 오류 발생: {e}")

def build_yaml_configs(csv_file_path):
    """CSV 스펙을 읽어 YAML 설정용 딕셔너리로 변환합니다."""
    crews_config = {}

    with open(csv_file_path, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            crew = row['crew_name']
            
            if crew not in crews_config:
                crews_config[crew] = {'agents': {}, 'tasks': {}}

            agent_key = row['task_agent']
            task_key = row.get('task_name', f"task_{agent_key}") # task_name이 없으면 자동 생성

            # Agents 설정 구성
            if agent_key not in crews_config[crew]['agents']:
                crews_config[crew]['agents'][agent_key] = {
                    'role': row['agent_role'],
                    'goal': row['agent_goal'],
                    'backstory': f"{row['agent_role']}로서, {row['agent_goal']} 달성을 위해 최선을 다합니다."
                }

            # Tasks 설정 구성
            crews_config[crew]['tasks'][task_key] = {
                'description': row['task_description'],
                'expected_output': row['task_expected_output'],
                'agent': agent_key,
                'tools': [row['task_tool']] if row['task_tool'] else []
            }
            
    return crews_config

def update_crew_files(crews_config):
    """생성된 스캐폴딩 내의 YAML 파일들을 스펙에 맞게 덮어씁니다."""
    for crew_name, config in crews_config.items():
        # CrewAI CLI(버전 0.30+ 기준)는 src/crew_name/config/ 하위에 yaml을 생성합니다.
        # 프로젝트 이름에서 '-'를 '_'로 변환한 패키지 폴더명을 찾습니다.
        package_name = crew_name.replace('-', '_')
        config_dir = Path(crew_name) / "src" / package_name / "config"
        
        if not config_dir.exists():
            print(f"[Warning] 설정 폴더를 찾을 수 없습니다: {config_dir}")
            continue

        agents_file = config_dir / "agents.yaml"
        tasks_file = config_dir / "tasks.yaml"

        # 1. agents.yaml 업데이트
        with open(agents_file, 'w', encoding='utf-8') as f:
            yaml.dump(config['agents'], f, allow_unicode=True, sort_keys=False)
            
        # 2. tasks.yaml 업데이트
        with open(tasks_file, 'w', encoding='utf-8') as f:
            yaml.dump(config['tasks'], f, allow_unicode=True, sort_keys=False)
            
        print(f"[Update] '{crew_name}'의 agents.yaml 및 tasks.yaml 파일 갱신 완료.")


def addon_files(crews_config) :
    """생성된 스캐폴딩에 후속 파일을 추가합니다."""
    
    # 1. devx_llm_wrapper.py 복사 (to src/[CREW_NAME]/)
    for crew_name, config in crews_config.items():
        package_name = crew_name.replace('-', '_')
        target_dir = Path(crew_name) / "src" / package_name
        if not target_dir.exists():
            print(f"[Warning] 대상 폴더를 찾을 수 없습니다: {target_dir}")
            continue
            
        target_file = target_dir / "devx_llm_wrapper.py"
        with open(target_file, 'w', encoding='utf-8') as f:
            f.write(open('../devx_llm_wrapper.py').read())
        print(f"[Copy] '{crew_name}'의 devx_llm_wrapper.py 파일 갱신 완료.")    
    
    # 2. env 파일 복사 (to .env)
    for crew_name, config in crews_config.items():
        target_dir = Path(crew_name)
        if not target_dir.exists():
            print(f"[Warning] 대상 폴더를 찾을 수 없습니다: {target_dir}")
            continue
            
        target_file = target_dir / ".env"
        with open(target_file, 'a', encoding='utf-8') as f:
            f.write(open('../env').read())
        print(f"[Copy] '{crew_name}'의 .env 파일 갱신 완료.")    


def main():
    csv_path = 'spec.csv'
    
    if not os.path.exists(csv_path):
        print(f"[{csv_path}] 파일을 찾을 수 없습니다.")
        return

    # 1. CSV 파싱하여 설정 데이터 추출
    crews_config = build_yaml_configs(csv_path)

    # 하위에 generated_crews 폴더를 만들고 그 하위에서 아래 작업을 한다.
    if not os.path.exists("generated_crews"):
        os.makedirs("generated_crews")
    os.chdir("generated_crews") 

    # 2. 파싱된 데이터를 바탕으로 각각의 Crew 스캐폴딩 및 파일 업데이트
    for crew_name in crews_config.keys():
        run_scaffolding(crew_name)
    
    # 3. 생성된 폴더 내 YAML 파일 덮어쓰기
    update_crew_files(crews_config)
    
    # 4. 후속 작업
    addon_files(crews_config)
    print("\n✅ 모든 자동화 애플리케이션 생성 프로세스가 완료되었습니다.")

if __name__ == "__main__":
    main()