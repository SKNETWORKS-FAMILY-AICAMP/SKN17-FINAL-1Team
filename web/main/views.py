import os
import json
import requests
import uuid
import base64
import boto3
import time
from io import BytesIO
from .models import Message
from datetime import datetime
from PIL import ImageOps,Image
from django.conf import settings
from django.shortcuts import render
from django.core.cache import cache
from django.http import JsonResponse
from .models import Gallery, Chat, Message
from django.core.files.base import ContentFile
from django.http import JsonResponse, StreamingHttpResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.core.files.uploadedfile import InMemoryUploadedFile


FASTAPI_URL = "http://69.30.85.245:22187/query"

# 이미지 리사이즈 함수
def resize_image(image_file, max_size=(1024, 1024), quality=100):
    """
    이미지를 리사이즈하고 최적화합니다.
    - max_size: 최대 크기 (width, height)
    - quality: JPEG 품질 (1-100)
    """
    try:
        img = Image.open(image_file)

        try:
            img = ImageOps.exif_transpose(img)
        except:
            pass

        original_width, original_height = img.size
        img.thumbnail(max_size, Image.Resampling.LANCZOS)
        if img.mode in ('RGBA', 'LA', 'P'):
            background = Image.new('RGB', img.size, (255, 255, 255))
            if img.mode == 'P':
                img = img.convert('RGBA')
            background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
            img = background
        elif img.mode != 'RGB':
            img = img.convert('RGB')

        output = BytesIO()
        img.save(output, format='JPEG', quality=quality, optimize=True)
        output.seek(0)

        return output
    except Exception as e:
        print(f"이미지 리사이즈 실패: {str(e)}")
        image_file.seek(0)
        return image_file

def main_view(request):
    return render(request, 'main/main.html')

@login_required
def gallery(request):
    user_id = request.user.id
    
    galleries = Gallery.objects.filter(user_id=user_id, is_deleted=False)

    return render(request, 'main/gallery.html', {'image_files': galleries,})

@login_required
def gallery_upload(request):
    user_id = request.user.id
    image_file = request.FILES.get('image')
    role = request.POST.get('role')

    if image_file:
        try:
            print(f"원본 이미지 크기: {image_file.size / 1024:.2f} KB")
            resized_image = resize_image(image_file, max_size=(1024, 1024), quality=100)

            unique_filename = f"{user_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}.jpg"

            resized_file = InMemoryUploadedFile(
                resized_image,
                None,
                unique_filename,
                'image/jpeg',
                resized_image.getbuffer().nbytes,
                None
            )

            print(f"리사이즈 후 크기: {resized_file.size / 1024:.2f} KB")
            print(f"S3 업로드 시작: {unique_filename}")

            gallery = Gallery(user_id=user_id)
            if role == 'user':
                gallery.is_deleted = True

            max_retries = 3
            retry_count = 0
            last_error = None

            while retry_count < max_retries:
                try:
                    gallery.image_path.save(unique_filename, resized_file, save=True)
                    print(f"이미지 S3 업로드 완료 - image_id: {gallery.image_id}, path: {gallery.image_path}")

                    return JsonResponse({
                        'success': True,
                        'message': "이미지 업로드 성공",
                        'image_id': gallery.image_id
                    })

                except Exception as upload_error:
                    retry_count += 1
                    last_error = upload_error
                    print(f"S3 업로드 실패 (시도 {retry_count}/{max_retries}): {str(upload_error)}")

                    if retry_count < max_retries:
                        time.sleep(1)  # 1초 대기 후 재시도
                        resized_image.seek(0)  # 파일 포인터 리셋
                    else:
                        raise last_error

        except Exception as e:
            import traceback
            error_detail = traceback.format_exc()
            print(f"이미지 업로드 최종 실패: {str(e)}")
            print(f"상세 에러:\n{error_detail}")

            error_message = "이미지 저장 중 문제 발생"
            if "timeout" in str(e).lower():
                error_message = "네트워크 타임아웃 - 다시 시도해주세요"
            elif "credentials" in str(e).lower() or "access" in str(e).lower():
                error_message = "서버 권한 오류 - 관리자에게 문의하세요"
            elif "bucket" in str(e).lower():
                error_message = "스토리지 연결 오류 - 잠시 후 다시 시도해주세요"

            return JsonResponse({'success': False, 'message': error_message})
    else:
        return JsonResponse({"success": True, "message": "저장할 이미지 없음"})

@login_required
def gallery_image_url(request, image_id):
    """이미지 ID로 이미지 URL 조회"""
    try:
        gallery_obj = Gallery.objects.get(image_id=image_id)

        # 이미지 URL 생성 (MEDIA_URL + 경로)
        if gallery_obj.image_path:
            image_url = gallery_obj.image_path.url
            return JsonResponse({
                'success': True,
                'image_url': image_url,
                'image_id': gallery_obj.image_id
            })
        else:
            return JsonResponse({'success': False, 'message': '이미지 경로가 없습니다.'})

    except Gallery.DoesNotExist:
        return JsonResponse({'success': False, 'message': '이미지를 찾을 수 없습니다.'})

@login_required
def gallery_delete(request):
    data = json.loads(request.body)
    image_id = data.get('image_id')

    try:
        del_gallery = Gallery.objects.get(image_id=image_id)
        del_gallery.is_deleted = True
        del_gallery.save()

        return JsonResponse(
            {'success': True, "message": "이미지 삭제 성공"}
        )
    except:
        return JsonResponse(
            {'success': False, "message": "이미지 삭제 오류!"}
        )

@login_required
@require_http_methods(["POST"])
def copy_profile_to_gallery(request):
    """프로필 이미지를 Gallery로 복사"""
    try:
        user = request.user

        if not user.profile_image:
            return JsonResponse({
                'success': False,
                'message': '프로필 이미지가 없습니다.'
            })

        s3_client = boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_S3_REGION_NAME
        )

        profile_key = user.profile_image.name

        buffer = BytesIO()
        s3_client.download_fileobj(
            settings.AWS_STORAGE_BUCKET_NAME,
            profile_key,
            buffer
        )
        buffer.seek(0)

        unique_filename = f"profile_{user.id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}.jpg"

        gallery = Gallery(user_id=user.id, is_deleted=True)
        gallery.image_path.save(unique_filename, buffer, save=True)

        return JsonResponse({
            'success': True,
            'image_id': gallery.image_id
        })

    except Exception as e:
        import traceback
        print(f"프로필 이미지 복사 실패: {str(e)}")
        print(traceback.format_exc())
        return JsonResponse({
            'success': False,
            'message': '프로필 이미지 복사 중 오류가 발생했습니다.'
        })

@login_required
def chat_list(request):
    """사용자의 채팅 기록 목록 조회"""
    user_id = request.user.id
    chats = Chat.objects.filter(user_id=user_id).order_by('-created_at')

    chat_list = [{
        'chat_id': chat.chat_id,
        'chat_title': chat.chat_title,
        'created_at': chat.created_at.strftime('%Y-%m-%d %H:%M:%S')
    } for chat in chats]

    return JsonResponse({'success': True, 'chats': chat_list})

@login_required
def chat_create(request):
    """새로운 채팅 생성"""
    if request.method == 'POST':
        data = json.loads(request.body)
        user_id = request.user.id
        message_text = data.get('message', '')

        chat_title = message_text[:15] if len(message_text) <= 15 else message_text[:15] + '...'

        # Chat 생성
        chat = Chat.objects.create(
            user_id=user_id,
            chat_title=chat_title
        )

        return JsonResponse({
            'success': True,
            'chat_id': chat.chat_id,
            'chat_title': chat.chat_title
        })

    return JsonResponse({'success': False, 'message': 'Invalid request method'})

@login_required
def chat_detail(request, chat_id):
    """특정 채팅의 메시지 조회"""
    try:
        chat = Chat.objects.get(chat_id=chat_id, user_id=request.user.id)
        messages = Message.objects.filter(chat=chat).order_by('created_at')

        message_list = []
        for msg in messages:
            message_data = {
                'message_id': msg.message_id,
                'is_answer': msg.is_answer,
                'content': msg.content,
                'created_at': msg.created_at.strftime('%Y-%m-%d %H:%M:%S')
            }

            if msg.image:
                message_data['image_url'] = msg.image.image_path.url

            message_list.append(message_data)

        return JsonResponse({
            'success': True,
            'chat_title': chat.chat_title,
            'messages': message_list
        })
    except Chat.DoesNotExist:
        return JsonResponse({'success': False, 'message': '채팅을 찾을 수 없습니다.'})

@login_required
def message_save(request):
    """메시지 저장"""
    if request.method == 'POST':
        data = json.loads(request.body)
        chat_id = data.get('chat_id')
        content = data.get('content')
        is_answer = data.get('is_answer', 'Q')
        image_id = data.get('image_id', None)

        try:
            chat = Chat.objects.get(chat_id=chat_id, user_id=request.user.id)

            # Message 생성
            message = Message.objects.create(
                chat=chat,
                content=content,
                is_answer=is_answer,
                image_id=image_id
            )

            return JsonResponse({
                'success': True,
                'message_id': message.message_id
            })
        except Chat.DoesNotExist:
            return JsonResponse({'success': False, 'message': '채팅을 찾을 수 없습니다.'})

    return JsonResponse({'success': False, 'message': 'Invalid request method'})

@login_required
def chat_update(request, chat_id):
    """채팅 제목 수정"""
    if request.method == 'POST':
        data = json.loads(request.body)
        chat_title = data.get('chat_title', '')

        if not chat_title or len(chat_title) > 15:
            return JsonResponse({'success': False, 'message': '채팅 이름은 1~15글자여야 합니다.'})

        try:
            chat = Chat.objects.get(chat_id=chat_id, user_id=request.user.id)
            chat.chat_title = chat_title
            chat.save()

            return JsonResponse({
                'success': True,
                'chat_title': chat.chat_title
            })
        except Chat.DoesNotExist:
            return JsonResponse({'success': False, 'message': '채팅을 찾을 수 없습니다.'})

    return JsonResponse({'success': False, 'message': 'Invalid request method'})

@login_required
def chat_delete(request, chat_id):
    """채팅 삭제"""
    if request.method == 'POST':
        try:
            chat = Chat.objects.get(chat_id=chat_id, user_id=request.user.id)
            chat.delete()

            return JsonResponse({'success': True})
        except Chat.DoesNotExist:
            return JsonResponse({'success': False, 'message': '채팅을 찾을 수 없습니다.'})

    return JsonResponse({'success': False, 'message': 'Invalid request method'})

@login_required
def check_response_complete(request, chat_id):
    """채팅의 응답 완료 여부 확인 및 최신 메시지 반환"""
    try:
        # 해당 채팅의 마지막 메시지 확인
        last_message = Message.objects.filter(chat_id=chat_id).order_by('-created_at').first()

        if not last_message:
            return JsonResponse({'success': False, 'complete': False, 'message': '메시지가 없습니다.'})

        # 마지막 메시지가 봇 응답(A)이면 완료된 것
        if last_message.is_answer == 'A':
            # 이미지가 있는 경우 URL 포함
            image_url = None
            if last_message.image_id:
                try:
                    gallery = Gallery.objects.get(image_id=last_message.image_id)
                    if gallery.image_path:
                        image_url = gallery.image_path.url
                except Gallery.DoesNotExist:
                    pass

            return JsonResponse({
                'success': True,
                'complete': True,
                'message': last_message.content,
                'image_url': image_url,
                'message_id': last_message.message_id
            })
        else:
            status_key = f'chat_status_{chat_id}'
            current_status = cache.get(status_key, '응답 생성 중...')

            return JsonResponse({
                'success': True,
                'complete': False,
                'status': current_status
            })

    except Exception as e:
        print(f"응답 완료 확인 오류: {str(e)}")
        return JsonResponse({'success': False, 'complete': False, 'message': str(e)})


@require_http_methods(["GET"])
def message_response(request):
    """SSE 스트리밍을 통한 실시간 상태 업데이트 및 응답 처리"""

    msg = request.GET.get("message", "").strip()
    image_id = request.GET.get("image_id")
    chat_id = request.GET.get("chat_id")
    user_id = request.user.id

    # 디버깅: 받은 데이터 확인
    print(f"받은 메시지: '{msg}'")
    print(f"받은 image_id: '{image_id}'")
    print(f"받은 chat_id: '{chat_id}'")

    # image_id가 존재하면 S3에서 이미지를 읽어서 base64 인코딩
    encoded_image = None
    if image_id and image_id.strip():
        try:
            gallery_obj = Gallery.objects.get(image_id=image_id)
            if gallery_obj.image_path:
                # S3에서 이미지 다운로드 (재시도 로직 추가)
                max_retries = 3
                retry_count = 0
                last_error = None

                while retry_count < max_retries:
                    try:
                        s3_client = boto3.client(
                            's3',
                            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                            region_name=settings.AWS_S3_REGION_NAME,
                            config=boto3.session.Config(
                                connect_timeout=5,
                                read_timeout=10,
                                retries={'max_attempts': 2}
                            )
                        )

                        s3_key = gallery_obj.image_path.name
                        print(f"S3에서 이미지 다운로드 시도 (#{retry_count + 1}): {s3_key}")

                        buffer = BytesIO()
                        s3_client.download_fileobj(
                            settings.AWS_STORAGE_BUCKET_NAME,
                            s3_key,
                            buffer
                        )
                        buffer.seek(0)
                        image_content = buffer.read()

                        file_ext = os.path.splitext(s3_key)[1].lower()
                        if file_ext in [".jpg", ".jpeg"]:
                            mime_type = "image/jpeg"
                        elif file_ext == ".png":
                            mime_type = "image/png"
                        elif file_ext == ".gif":
                            mime_type = "image/gif"
                        else:
                            mime_type = "image/jpeg" 

                        encoded_image = f"data:{mime_type};base64,{base64.b64encode(image_content).decode('utf-8')}"
                        print(f"S3 이미지를 base64로 인코딩 완료: {s3_key}")
                        break 

                    except Exception as download_error:
                        retry_count += 1
                        last_error = download_error
                        print(f"S3 다운로드 실패 (시도 {retry_count}/{max_retries}): {str(download_error)}")

                        if retry_count < max_retries:
                            import time
                            time.sleep(1)
                        else:
                            raise last_error

        except Gallery.DoesNotExist:
            print(f"이미지 ID {image_id}를 찾을 수 없습니다.")
        except Exception as e:
            print(f"S3 이미지 다운로드 최종 실패: {str(e)}")
            import traceback
            traceback.print_exc()

    fastapi_stream_url = f"{FASTAPI_URL}/stream"
    session_id = f"{request.user.id}_{chat_id}" if chat_id else f"{request.user.id}"

    payload = {
        "query": msg,
        "session_id": session_id,
    }
    if encoded_image:
        payload["image_path"] = encoded_image

    print(f"➡ FastAPI SSE 호출 (POST): {fastapi_stream_url}")
    print(f"➡ Payload keys: {list(payload.keys())}")
    if encoded_image:
        print(f"➡ 이미지 데이터 길이: {len(encoded_image)} bytes")

    def event_stream():
        """SSE 이벤트를 Django에서 클라이언트로 전달"""
        try:
            # POST 요청으로 변경 (JSON body 사용)
            with requests.post(
                fastapi_stream_url,
                json=payload,
                stream=True,
                timeout=300,
                headers={'Content-Type': 'application/json'}
            ) as response:
                response.raise_for_status()

                bot_message = ""
                generated_image_id = None

                for line in response.iter_lines(decode_unicode=True):
                    if line.startswith('data: '):
                        data_str = line[6:]
                        try:
                            event_data = json.loads(data_str)
                            event_type = event_data.get("type")

                            if event_type == "status":
                                status_key = f'chat_status_{chat_id}'
                                cache.set(status_key, event_data['message'], timeout=300)

                                yield f"data: {json.dumps({'type': 'status', 'message': event_data['message']}, ensure_ascii=False)}\n\n"

                            elif event_type == "response":
                                bot_message = event_data.get("output", "")
                                generated_image = event_data.get("generated_image")

                                if generated_image:
                                    try:
                                        if generated_image.startswith("data:"):
                                            base64_data = generated_image.split(",", 1)[1]
                                        else:
                                            base64_data = generated_image
                                        image_binary = base64.b64decode(base64_data)

                                        max_retries = 3
                                        retry_count = 0
                                        last_error = None

                                        while retry_count < max_retries:
                                            try:
                                                gallery = Gallery(user_id=request.user.id, is_deleted=False)
                                                filename = f"generated_{request.user.id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}.jpg"

                                                print(f"생성된 이미지 S3 업로드 시도 (#{retry_count + 1}): {filename}")

                                                gallery.image_path.save(filename, ContentFile(image_binary), save=True)
                                                generated_image_id = gallery.image_id

                                                print(f"생성된 이미지 S3 저장 완료 - image_id: {generated_image_id}")
                                                break  # 성공하면 루프 탈출

                                            except Exception as save_error:
                                                retry_count += 1
                                                last_error = save_error
                                                print(f"생성된 이미지 저장 실패 (시도 {retry_count}/{max_retries}): {str(save_error)}")

                                                if retry_count < max_retries:
                                                    import time
                                                    time.sleep(1)
                                                else:
                                                    raise last_error

                                    except Exception as e:
                                        import traceback
                                        error_detail = traceback.format_exc()
                                        print(f"생성된 이미지 저장 최종 실패: {str(e)}")
                                        print(f"상세 에러:\n{error_detail}")

                                if chat_id:
                                    try:
                                        Message.objects.create(
                                            chat_id=chat_id,
                                            content=bot_message,
                                            is_answer='A',
                                            image_id=generated_image_id if generated_image_id else None
                                        )
                                        print(f"✅ 챗봇 응답 DB 저장 완료 - chat_id: {chat_id}, image_id: {generated_image_id}")
                                    except Exception as save_error:
                                        print(f"❌ 챗봇 응답 DB 저장 실패: {str(save_error)}")
                                        import traceback
                                        traceback.print_exc()

                                status_key = f'chat_status_{chat_id}'
                                cache.delete(status_key)

                                yield f"data: {json.dumps({'type': 'response', 'response': bot_message, 'generated_image_id': generated_image_id}, ensure_ascii=False)}\n\n"

                            elif event_type == "error":
                                status_key = f'chat_status_{chat_id}'
                                cache.delete(status_key)

                                yield f"data: {json.dumps({'type': 'error', 'message': event_data['message']}, ensure_ascii=False)}\n\n"

                        except json.JSONDecodeError:
                            continue

        except Exception as e:
            print(f"FastAPI SSE 스트림 오류: {str(e)}")
            yield f"data: {json.dumps({'type': 'error', 'message': f'서버 오류: {str(e)}'}, ensure_ascii=False)}\n\n"

        yield f"data: {json.dumps({'type': 'done'}, ensure_ascii=False)}\n\n"

    return StreamingHttpResponse(event_stream(), content_type='text/event-stream')
