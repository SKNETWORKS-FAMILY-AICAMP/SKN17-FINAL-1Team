import json
import os
from django.core.management.base import BaseCommand
from pictorial_book.models import HairStyleDictionary


class Command(BaseCommand):
    help = "Update pictorial book descriptions from JSON file"

    def handle(self, *args, **kwargs):
        # JSON 파일 경로
        json_file_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            'DB',
            'hairstyle_descriptions_VER1.json'
        )

        self.stdout.write(self.style.WARNING(f"JSON 파일 로드 중: {json_file_path}"))

        try:
            # JSON 파일 읽기
            with open(json_file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # 카테고리 매핑 (C: 커트, P: 펌, R: 염색)
            categories = {
                'C': data.get('C', {}),
                'P': data.get('P', {}),
                'R': data.get('R', {})
            }

            total_updated = 0
            total_not_found = 0

            # 각 카테고리별로 처리
            for category_code, category_data in categories.items():
                self.stdout.write(self.style.SUCCESS(f"\n[{category_code}] 카테고리 처리 중..."))

                # 성별별로 처리 (M: 남성, F: 여성, N: 중성)
                for gender_code, styles in category_data.items():
                    self.stdout.write(f"  - 성별: {gender_code}")

                    # 각 스타일별로 처리
                    for style_name, description in styles.items():
                        try:
                            # 데이터베이스에서 해당 레코드 찾기
                            dict_obj = HairStyleDictionary.objects.filter(
                                name=style_name,
                                category=category_code,
                                gender=gender_code
                            ).first()

                            if dict_obj:
                                # description 업데이트
                                dict_obj.description = description
                                dict_obj.save()
                                total_updated += 1
                                self.stdout.write(
                                    self.style.SUCCESS(
                                        f"    [OK] 업데이트: {category_code}/{gender_code}/{style_name}"
                                    )
                                )
                            else:
                                total_not_found += 1
                                self.stdout.write(
                                    self.style.WARNING(
                                        f"    - DB에 없음: {category_code}/{gender_code}/{style_name}"
                                    )
                                )

                        except Exception as e:
                            self.stdout.write(
                                self.style.ERROR(
                                    f"    [ERROR] 에러: {category_code}/{gender_code}/{style_name} - {str(e)}"
                                )
                            )

            # 결과 요약
            self.stdout.write(self.style.SUCCESS(f"\n{'='*60}"))
            self.stdout.write(self.style.SUCCESS(f"완료!"))
            self.stdout.write(self.style.SUCCESS(f"총 업데이트: {total_updated}개"))
            self.stdout.write(self.style.WARNING(f"DB에 없음: {total_not_found}개"))

        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f"JSON 파일을 찾을 수 없습니다: {json_file_path}"))
        except json.JSONDecodeError as e:
            self.stdout.write(self.style.ERROR(f"JSON 파싱 에러: {str(e)}"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"에러 발생: {str(e)}"))
