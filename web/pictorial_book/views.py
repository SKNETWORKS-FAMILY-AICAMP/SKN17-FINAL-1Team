from django.http import JsonResponse
from django.core.files.storage import default_storage
from .models import HairStyleDictionary, HairStyleImage


def get_hair_images(request):
    # Step 1. 프론트에서 전달받은 값
    gender = request.GET.get("gender")         # male / female / none
    category = request.GET.get("category")     # cut / perm / color
    name = request.GET.get("name")             # 예: 가일컷

    # Step 2. JS 코드 값을 DB 코드로 변환
    gender_map = {
        "male": "M",
        "female": "F",
        "none": "N"
    }

    category_map = {
        "cut": "C",
        "perm": "P",
        "color": "R"
    }

    gender_code = gender_map.get(gender)
    category_code = category_map.get(category)

    if not gender_code or not category_code:
        return JsonResponse({"images": []})

    # Step 3. HairStyleDictionary에서 해당 스타일 찾기
    try:
        style = HairStyleDictionary.objects.get(
            name=name,
            gender=gender_code,
            category=category_code
        )
    except HairStyleDictionary.DoesNotExist:
        return JsonResponse({"images": []})

    # Step 4. 해당 스타일의 이미지 목록 가져오기
    images = HairStyleImage.objects.filter(name_gender=style)

    result = []

    for img in images:
        # DB에는 "pictorial_book/male/가일컷/숏/1.jpg" 형태로 저장되어 있음
        relative_path = img.image_path

        # S3 URL 생성
        url = default_storage.url(relative_path)

        result.append({
            "length": img.length,
            "url": url
        })

    return JsonResponse({
        "images": result,
        "description": style.description
    })


def get_hair_list(request):
    gender_param = request.GET.get("gender")      # male / female / none
    category_param = request.GET.get("category")  # cut / perm / color

    gender_map = {"male": "M", "female": "F", "none": "N"}
    category_map = {"cut": "C", "perm": "P", "color": "R"}

    gender_code = gender_map.get(gender_param)
    category_code = category_map.get(category_param)

    # DB에서 gender + category 에 해당하는 모든 스타일 조회
    styles = HairStyleDictionary.objects.filter(
        gender=gender_code,
        category=category_code
    )

    # 초성별 그룹핑
    result = {}

    def get_initial(name):
        char = name[0]
        code = ord(char) - 44032
        if code < 0 or code > 11171:
            return None
        initials = ["ㄱ","ㄲ","ㄴ","ㄷ","ㄸ","ㄹ","ㅁ","ㅂ","ㅃ","ㅅ","ㅆ","ㅇ","ㅈ","ㅉ","ㅊ","ㅋ","ㅌ","ㅍ","ㅎ"]
        return initials[code // 588]

    for style in styles:
        initial = get_initial(style.name)
        if initial:
            result.setdefault(initial, []).append(style.name)

    return JsonResponse(result)
