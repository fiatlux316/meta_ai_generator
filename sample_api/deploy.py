import os
import sys
import zipfile
import argparse
import tempfile
import requests

def zip_directory(source_dir, crew_name, output_zip_path):
    # 압축 제외 디렉토리 정의 (가상환경, Git, 의존성, 빌드 산출물 등)
    exclude_dirs = {'.venv', 'venv', '__pycache__', '.git', 'tests', 'node_modules', '.venv-docker', '.venv-docker-worker'}
    
    with zipfile.ZipFile(output_zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(source_dir):
            # dirs 리스트를 in-place 수정하여 os.walk가 해당 폴더들을 재귀 탐색하지 않도록 함 (오버헤드 방지)
            dirs[:] = [d for d in dirs if d not in exclude_dirs]
            for file in files:
                file_path = os.path.join(root, file)
                # ZIP 내부 보존 구조를 위해 상대 경로 계산
                arcname = os.path.relpath(file_path, source_dir)
                # 최상위에 crew_name 폴더가 감싸지도록 arcname 변경
                arcname_with_root = os.path.join(crew_name, arcname)
                zipf.write(file_path, arcname_with_root)

def main():
    amp_url = os.environ.get("CREWAI_AMP_URL") or os.environ.get("AMP_URL") or "http://localhost:8000"
    amp_key = os.environ.get("CREWAI_AMP_KEY") or os.environ.get("CREWAI_API_KEY") or os.environ.get("AMP_KEY") or "super-secret-company-key"

    parser = argparse.ArgumentParser(description="Deploy CrewAI Application to Private AMP")
    parser.add_argument("--dir", "-d", default=".", help="Directory of the Crew application to deploy (default: current directory)")
    parser.add_argument("--overwrite", "-o", action="store_true", help="Force overwrite if the crew already exists on the server")
    args = parser.parse_args()

    source_dir = os.path.abspath(args.dir)
    if not os.path.isdir(source_dir):
        print(f"Error: Directory '{source_dir}' does not exist.")
        sys.exit(1)
        
    # 패키지 명칭 설정 (최하단 폴더 명)
    crew_name = os.path.basename(source_dir.rstrip('/'))
    if not crew_name:
        crew_name = "crew_application"
        
    print(f"🚀 Packaging crew '{crew_name}' from {source_dir}...")

    # 임시 ZIP 파일 생성
    with tempfile.NamedTemporaryFile(delete=False, suffix=".zip") as tmp:
        tmp_zip_path = tmp.name
        
    try:
        # ZIP 압축 수행
        zip_directory(source_dir, crew_name, tmp_zip_path)
        zip_size_mb = os.path.getsize(tmp_zip_path) / (1024 * 1024)
        print(f"📦 Created ZIP archive ({zip_size_mb:.2f} MB)")
        
        # Deploy API 요청
        deploy_url = f"{amp_url.rstrip('/')}/api/v1/crews/deploy"
        headers = {
            "Authorization": f"Bearer {amp_key}"
        }
        params = {
            "overwrite": "true" if args.overwrite else "false"
        }
        
        print(f"📡 Uploading and deploying to {deploy_url}...")
        with open(tmp_zip_path, 'rb') as f:
            files = {
                "file": (f"{crew_name}.zip", f, "application/zip")
            }
            response = requests.post(deploy_url, headers=headers, params=params, files=files)
            
        if response.status_code == 201:
            res_data = response.json()
            print("✅ Deployment Successful!")
            print(f"  - Crew ID: {res_data['crew']['crew_id']}")
            print(f"  - Display Name: {res_data['crew']['display_name']}")
            print(f"  - Parsed default inputs: {res_data['crew']['default_inputs']}")
        elif response.status_code == 409:
            print(f"⚠️ Deployment Conflict: Crew '{crew_name}' already exists on the server.")
            print("  Use '-o' or '--overwrite' flag to overwrite the existing application.")
            sys.exit(1)
        else:
            print(f"❌ Deployment Failed (HTTP {response.status_code})")
            try:
                print(response.json().get("detail", response.text))
            except Exception:
                print(response.text)
            sys.exit(1)
            
    except Exception as e:
        print(f"❌ Error during deployment: {e}")
        sys.exit(1)
    finally:
        if os.path.exists(tmp_zip_path):
            os.remove(tmp_zip_path)

if __name__ == "__main__":
    main()
