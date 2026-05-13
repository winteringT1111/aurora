import csv
import json
import os
import sys
import django

# 1. Django 환경 설정
# 'myproject.settings' 부분을 실제 프로젝트 폴더명에 맞춰 수정하세요.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings') 
django.setup()

from exploration.models import ExplorationMap

# 2. 대용량 CSV 처리를 위한 필드 제한 해제
# Base64 이미지가 포함된 text 필드는 매우 길기 때문에 이 설정이 필수입니다.
try:
    csv.field_size_limit(sys.maxsize)
except OverflowError:
    # 32비트 C long의 최대값인 2147483647로 설정합니다.
    csv.field_size_limit(2147483647)

def run_import():
    file_path = 'exploration_explorationmap.csv'  # 가져올 CSV 파일명
    
    if not os.path.exists(file_path):
        print(f"❌ 에러: {file_path} 파일을 찾을 수 없습니다.")
        return

    print("🚀 데이터베이스 통합 및 가져오기 시작...")

    try:
        with open(file_path, mode='r', encoding='utf-8') as f:
            # CSV의 첫 줄(헤더)을 기준으로 데이터를 읽습니다.
            reader = csv.DictReader(f)
            success_count = 0
            error_count = 0
            
            for row in reader:
                try:
                    # image_1cab19.png의 구조에 맞춰 데이터 파싱
                    map_id = row.get('id')
                    title = row.get('title', '무제')
                    
                    # content_data가 JSON 문자열인 경우 파싱 시도
                    try:
                        content_json = json.loads(row['content_data'])
                    except (json.JSONDecodeError, TypeError):
                        # 이미 JSON 형태이거나 형식이 잘못된 경우 처리
                        content_json = row['content_data']

                    # 데이터 생성 또는 업데이트 (ID 기준)
                    obj, created = ExplorationMap.objects.update_or_create(
                        id=map_id,
                        defaults={
                            'title': title,
                            'content_data': content_json,
                            # created_at, updated_at은 auto_now_add 설정에 따라 자동 생성되거나 
                            # 필요시 아래처럼 명시적으로 넣을 수 있습니다.
                            # 'created_at': row.get('created_at'),
                        }
                    )
                    
                    verb = "생성" if created else "업데이트"
                    print(f"✅ [ID {map_id}] {title} - {verb} 완료")
                    success_count += 1
                    
                except Exception as e:
                    print(f"❌ [ID {row.get('id', 'Unknown')}] 처리 중 에러: {str(e)}")
                    error_count += 1

            print("-" * 30)
            print(f"🎉 작업 완료!")
            print(f"📊 성공: {success_count}건 / 실패: {error_count}건")

    except Exception as e:
        print(f"🔥 파일 읽기 중 치명적 에러: {str(e)}")

if __name__ == "__main__":
    run_import()