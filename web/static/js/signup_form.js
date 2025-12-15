document.addEventListener('DOMContentLoaded', function() {
    // DOM 요소들
    const emailId = document.getElementById('emailId');
    const domainSelect = document.getElementById('domainSelect');
    const customDomain = document.getElementById('customDomain');
    const sendCodeBtn = document.getElementById('sendCodeBtn');
    const verifyCode = document.getElementById('verifyCode');
    const timer = document.getElementById('timer');
    const verifyCodeBtn = document.getElementById('verifyCodeBtn');
    const verifyError = document.getElementById('verifyError');
    const verifySuccess = document.getElementById('verifySuccess');
    const emailHelperText = document.getElementById('emailHelperText');
    const domainSelectWrapper = document.querySelector('.domain-select-wrapper');

    const password = document.getElementById('password');
    const passwordError = document.getElementById('passwordError');
    const passwordSuccess = document.getElementById('passwordSuccess');
    const passwordConfirm = document.getElementById('passwordConfirm');
    const passwordConfirmError = document.getElementById('passwordConfirmError');
    const passwordConfirmSuccess = document.getElementById('passwordConfirmSuccess');

    const nickname = document.getElementById('nickname');
    const nicknameError = document.getElementById('nicknameError');
    const nicknameSuccess = document.getElementById('nicknameSuccess');

    const profilePreview = document.getElementById('profilePreview');
    const profileImage = document.getElementById('profileImage');
    const previewImg = document.getElementById('previewImg');
    const plusIcon = document.querySelector('.plus-icon');
    const profileError = document.getElementById('profileError');
    const removeProfileBtn = document.getElementById('removeProfileBtn');

    const cancelBtn = document.getElementById('cancelBtn');
    const submitBtn = document.getElementById('submitBtn');
    const overallError = document.getElementById('overallError');
    const signupForm = document.getElementById('signupForm');

    // 확인 모달 요소들
    const confirmModal = document.getElementById('confirmModal');
    const confirmMessage = document.getElementById('confirmMessage');
    const confirmBtn = document.getElementById('confirmBtn');

    // 확인 모달 표시 함수
    function showConfirmModal(message) {
        if (confirmMessage) {
            confirmMessage.textContent = message;
        }
        if (confirmModal) {
            confirmModal.classList.add('show');
        }
    }

    // 확인 버튼 클릭 이벤트
    if (confirmBtn) {
        confirmBtn.addEventListener('click', function() {
            if (confirmModal) {
                confirmModal.classList.remove('show');
            }
        });
    }

    // 상태 변수들
    let timerInterval = null;
    let timeLeft = 180; // 3분
    let isEmailVerified = false;
    let isCodeSent = false;
    let isTimeExpired = false; // 시간 만료 여부

    // 이메일 입력 체크
    function checkEmailInput() {
        const emailValue = emailId.value.trim();
        const domainValue = domainSelect.value === 'custom' ? customDomain.value.trim() : domainSelect.value;
        
        if (emailValue.length > 0 && domainValue.length > 0) {
            sendCodeBtn.disabled = false;
            sendCodeBtn.style.cursor = 'pointer';
            sendCodeBtn.style.backgroundColor = '#FEF9D9';
        } else {
            sendCodeBtn.disabled = true;
            sendCodeBtn.style.cursor = 'not-allowed';
            sendCodeBtn.style.backgroundColor = '#ccc';
        }
    }

    customDomain.style.display = 'none';

    // 도메인 선택 변경
    domainSelect.addEventListener('change', function() {

        if (this.value === 'custom') {
            domainSelectWrapper.style.display = 'none';
            customDomain.style.display = 'block';
            customDomain.disabled = false;
            customDomain.value = '';
            customDomain.focus();
        } else {
            // 일반 도메인 선택 시
            customDomain.style.display = 'none';
            customDomain.value = '';
        }

        // 이메일 수정 시 인증코드 발송 버튼으로 리셋
        if (isCodeSent) {
            resetVerification();
        }
        checkEmailInput();
    });

    customDomain.addEventListener('blur', function() {
        // 입력값이 비어있으면 다시 선택 박스로 복귀
        if (this.value.trim() === '') {
            this.style.display = 'none';
            domainSelectWrapper.style.display = 'block';
            domainSelect.value = '';
        }
    
        checkEmailInput();
    });

    customDomain.addEventListener('input', function() {
        // 직접 입력 도메인
        if (typeof isCodeSent !== 'undefined' && isCodeSent) {
            resetVerification();
        }
        // 에러 메시지가 있으면 초기화
        if (emailHelperText.textContent && emailHelperText.style.color === '#ff6b4a') {
            emailHelperText.textContent = '';
            emailHelperText.style.color = '';
        }
        checkEmailInput();
    });

    // 직접입력 도메인에서 포커스 아웃시 select로 돌아가기
    customDomain.addEventListener('blur', function() {
        if (this.value === '') {
            this.style.display = 'none';
            domainSelect.style.display = 'block';
            domainSelect.value = '';
        }
    });

    // 이메일 ID 입력
    emailId.addEventListener('input', function() {
        if (isCodeSent) {
            resetVerification();
        }
        // 에러 메시지가 있으면 초기화
        if (emailHelperText.textContent && emailHelperText.style.color === '#ff6b4a') {
            emailHelperText.textContent = '';
            emailHelperText.style.color = '';
        }
        checkEmailInput();
    });

    // 이메일 유효성 검사
    function validateEmail() {
        const emailValue = emailId.value.trim();
        let domainValue = '';

        // select가 보이는 경우 select의 값 사용, input이 보이는 경우 input의 값 사용
        if (domainSelect.style.display === 'none') {
            domainValue = customDomain.value.trim();
        } else {
            domainValue = domainSelect.value;
        }

        if (!emailValue || !domainValue) {
            emailHelperText.textContent = '';
            emailHelperText.style.color = '';
            sendCodeBtn.disabled = true;
            sendCodeBtn.style.cursor = 'not-allowed';
            sendCodeBtn.style.backgroundColor = '#ccc';
            return false;
        }

        // 이메일 형식 검증
        const emailRegex = /^[a-zA-Z0-9._-]+$/;
        const domainRegex = /^[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;

        if (!emailRegex.test(emailValue)) {
            emailHelperText.textContent = '올바른 이메일 형식이 아닙니다.';
            emailHelperText.style.color = '#ff6b4a';
            sendCodeBtn.disabled = true;
            sendCodeBtn.style.cursor = 'not-allowed';
            sendCodeBtn.style.backgroundColor = '#ccc';
            return false;
        }

        // 직접 입력인 경우 도메인 형식 검사
        if (domainSelect.value === 'custom') {
            if (!domainRegex.test(domainValue)) {
                emailHelperText.textContent = '올바른 도메인 형식이 아닙니다.';
                emailHelperText.style.color = '#ff6b4a';
                sendCodeBtn.disabled = true;
                sendCodeBtn.style.cursor = 'not-allowed';
                sendCodeBtn.style.backgroundColor = '#ccc';
                return false;
            }
        }

        emailHelperText.textContent = '';
        emailHelperText.style.color = '';
        return true;
    }

    // 인증 리셋
    function resetVerification() {
        isCodeSent = false;
        isEmailVerified = false;
        isTimeExpired = false; // 시간 만료 상태 초기화
        sendCodeBtn.textContent = '인증코드 발송';
        sendCodeBtn.style.backgroundColor = '#FEF9D9';
        sendCodeBtn.style.cursor = 'pointer';
        sendCodeBtn.classList.remove('resend-btn');
        verifyCode.value = '';
        verifyCode.disabled = true;
        verifyError.classList.remove('show');
        verifyError.textContent = '';
        verifySuccess.classList.remove('show');
        emailHelperText.textContent = '';
        timer.textContent = '';

        if (timerInterval) {
            clearInterval(timerInterval);
            timerInterval = null;
        }

        // 폼 필드 비활성화
        password.disabled = true;
        password.value = '';
        passwordConfirm.disabled = true;
        passwordConfirm.value = '';
        nickname.disabled = true;
        nickname.value = '';

        // 에러 메시지 초기화
        passwordError.classList.remove('show');
        passwordSuccess.classList.remove('show');
        passwordConfirmError.classList.remove('show');
        passwordConfirmSuccess.classList.remove('show');
        nicknameError.classList.remove('show');
        nicknameSuccess.classList.remove('show');

        checkSubmitBtn();
    }

    // 인증코드 발송 버튼 클릭
    sendCodeBtn.addEventListener('click', async function() {
        if (this.disabled) return;

        // 이메일 유효성 검사
        if (!validateEmail()) {
            return;
        }

        try {
            // 발송버튼 일시적으로 막기
            sendCodeBtn.disabled = true;
            sendCodeBtn.style.cursor = 'not-allowed';
            sendCodeBtn.style.backgroundColor = '#ccc';

            const domainValue = domainSelect.value === 'custom' ? customDomain.value.trim() : domainSelect.value;
            const fullEmail = emailId.value.trim() + '@' + domainValue;
            
            // 서버에 인증코드 발송 요청
            const response = await fetch('/uauth/send-verification-code/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ email: fullEmail })
            });
            
            const data = await response.json();
            
            if (data.success) {
                const isResend = isCodeSent; // 재발송인지 확인
                isCodeSent = true;
                isTimeExpired = false; // 새 코드 발송 시 시간 만료 상태 초기화
                this.textContent = '코드 재발송';
                this.classList.add('resend-btn');

                // 3초 후 버튼 다시 활성화

                sendCodeBtn.disabled = false;
                sendCodeBtn.style.cursor = 'pointer';
                sendCodeBtn.style.backgroundColor = 'rgba(250, 176, 169, 0.3)';


                // 인증코드 입력창 활성화
                verifyCode.disabled = false;
                verifyCode.value = '';
                verifyCode.style.cursor = 'text';
                verifyCode.style.backgroundColor = '#fff';
                verifyCode.focus();

                // 타이머 시작
                timeLeft = 180;
                startTimer();
                
                // 안내 메시지 (처음 발송 vs 재발송)
                if (isResend) {
                    emailHelperText.textContent = '인증코드가 재발송되었습니다. 3분 안에 인증코드를 정확히 입력해주세요';
                } else {
                    emailHelperText.textContent = '인증코드가 발송되었습니다. 3분 안에 인증코드를 정확히 입력해주세요';
                }
                
                // 에러/성공 메시지 초기화
                verifyError.classList.remove('show');
                verifySuccess.classList.remove('show');
                verifyCodeBtn.disabled = true;
            } else {
                emailHelperText.textContent = data.message || '인증코드 발송에 실패했습니다.';
                emailHelperText.style.color = '#ff6b4a';
                // 에러 발생 시 버튼 비활성화 유지 (이메일 수정 시 다시 활성화됨)
                sendCodeBtn.disabled = true;
                sendCodeBtn.style.cursor = 'not-allowed';
                sendCodeBtn.style.backgroundColor = '#ccc';
            }
        } catch (error) {
            console.error('Error:', error);
            emailHelperText.textContent = '인증코드 발송 중 오류가 발생했습니다.';
            emailHelperText.style.color = '#ff6b4a';
            sendCodeBtn.disabled = true;
            sendCodeBtn.style.cursor = 'not-allowed';
            sendCodeBtn.style.backgroundColor = '#ccc';
        }
    });

    // 타이머 시작
    function startTimer() {
        if (timerInterval) {
            clearInterval(timerInterval);
        }
        
        updateTimerDisplay();
        
        timerInterval = setInterval(function() {
            timeLeft--;
            updateTimerDisplay();

            if (timeLeft <= 0) {
                clearInterval(timerInterval);
                isTimeExpired = true; // 시간 만료 표시
                verifyCodeBtn.disabled = true; // 인증 버튼 비활성화
                verifyError.textContent = '인증시간이 만료되었습니다. 코드를 다시 발급받아 주세요.';
                verifyError.classList.add('show');
                verifySuccess.classList.remove('show');
                verifyCode.disabled = true;
                verifyCode.value = '';
                verifyCode.style.cursor = 'not-allowed';
                verifyCode.style.backgroundColor = '#D9D9D9';
            }
        }, 1000);
    }

    // 타이머 표시 업데이트
    function updateTimerDisplay() {
        const minutes = Math.floor(timeLeft / 60);
        const seconds = timeLeft % 60;
        timer.textContent = `${minutes}: ${seconds.toString().padStart(2, '0')}`;
    }

    // 인증코드 입력
    verifyCode.addEventListener('input', function() {
        // 시간이 만료되었으면 버튼 활성화하지 않음
        if (isTimeExpired) {
            verifyCodeBtn.disabled = true;
            return;
        }

        if (this.value.trim().length > 0) {
            verifyCodeBtn.disabled = false;
        } else {
            verifyCodeBtn.disabled = true;
        }
    });

    // 인증코드 확인 버튼 클릭
    verifyCodeBtn.addEventListener('click', async function() {
        if (this.disabled) return;
        
        if (timeLeft <= 0) {
            verifyError.textContent = '인증시간이 만료되었습니다. 코드를 다시 발급받아 주세요.';
            verifyError.classList.add('show');
            verifySuccess.classList.remove('show');
            return;
        }
        
        try {
            // 이메일 조합
            const domainValue = domainSelect.value === 'custom' ? customDomain.value.trim() : domainSelect.value;
            const fullEmail = emailId.value.trim() + '@' + domainValue;
            
            // 서버에 인증코드 확인 요청
            const response = await fetch('/uauth/verify-code/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    email: fullEmail,
                    code: verifyCode.value
                })
            });
            
            const data = await response.json();
            
            if (data.success) {
                // 인증 성공
                isEmailVerified = true;
                verifySuccess.textContent = '인증이 완료되었습니다.';
                verifySuccess.classList.add('show');
                verifyError.classList.remove('show');
                verifyCodeBtn.disabled = true;
                sendCodeBtn.disabled = true;
                sendCodeBtn.style.cursor = 'not-allowed';
                sendCodeBtn.style.backgroundColor = '#ccc';
                emailHelperText.textContent = '';
                
                // 타이머 정지
                if (timerInterval) {
                    clearInterval(timerInterval);
                }
                
                // 폼 필드 활성화
                password.disabled = false;
                passwordConfirm.disabled = false;
                nickname.disabled = false;
                
                // 이메일 필드 비활성화
                sendCodeBtn.disabled = true;
                sendCodeBtn.textContent = "인증코드 발송";
                sendCodeBtn.classList.remove('resend-btn');
                verifyCode.disabled = true;
                
                checkSubmitBtn();
            } else {
                // 인증 실패
                isEmailVerified = false;
                verifyError.textContent = data.message || '인증코드가 일치하지 않습니다.';
                verifyError.classList.add('show');
                verifySuccess.classList.remove('show');
            }
        } catch (error) {
            console.error('Error:', error);
            verifyError.textContent = '인증 확인 중 오류가 발생했습니다.';
            verifyError.classList.add('show');
            verifySuccess.classList.remove('show');
        }
    });

    // 비밀번호 유효성 검사
    function validatePassword(pw) {
        // 8~15자, 영어 대소문자/숫자/특수문자 중 세 가지 이상
        const hasUpperCase = /[A-Z]/.test(pw);
        const hasLowerCase = /[a-z]/.test(pw);
        const hasNumber = /[0-9]/.test(pw);
        const hasSpecial = /[!@#$%^&*(),.?":{}|<>]/.test(pw);
        
        const typeCount = [hasUpperCase, hasLowerCase, hasNumber, hasSpecial].filter(Boolean).length;
        
        return pw.length >= 8 && pw.length <= 15 && typeCount >= 3;
    }

    // 비밀번호 입력
    password.addEventListener('input', function() {
        if (this.value.length > 0 && !validatePassword(this.value)) {
            passwordError.textContent = '사용 불가능한 비밀번호입니다.';
            passwordError.classList.add('show');
            passwordSuccess.classList.remove('show');
        } else if (this.value.length > 0 && validatePassword(this.value)) {
            passwordError.classList.remove('show');
            passwordSuccess.textContent = '사용 가능한 비밀번호입니다.';
            passwordSuccess.classList.add('show');
        } else {
            passwordError.classList.remove('show');
            passwordSuccess.classList.remove('show');
        }
        
        // 비밀번호 확인 체크
        if (passwordConfirm.value.length > 0) {
            checkPasswordMatch();
        }
        checkSubmitBtn();
    });

    // 비밀번호 확인 입력
    passwordConfirm.addEventListener('input', function() {
        checkPasswordMatch();
        checkSubmitBtn();
    });

    // 비밀번호 일치 확인
    function checkPasswordMatch() {
        if (passwordConfirm.value.length > 0 && password.value !== passwordConfirm.value) {
            passwordConfirmError.textContent = '비밀번호가 일치하지 않습니다.';
            passwordConfirmError.classList.add('show');
            passwordConfirmSuccess.classList.remove('show');
        } else if (passwordConfirm.value.length > 0 && password.value === passwordConfirm.value) {
            passwordConfirmError.classList.remove('show');
            passwordConfirmSuccess.textContent = '비밀번호가 일치합니다.';
            passwordConfirmSuccess.classList.add('show');
        } else {
            passwordConfirmError.classList.remove('show');
            passwordConfirmSuccess.classList.remove('show');
        }
    }

    // 닉네임 유효성 검사
    function validateNickname(nick) {
        // 영어/한글로 구성된 2~10자
        const regex = /^[a-zA-Zㄱ-ㅎㅏ-ㅣ가-힣]{2,10}$/;
        return regex.test(nick);
    }

    // 닉네임 입력
    nickname.addEventListener('input', function() {
        if (this.value.length > 0 && !validateNickname(this.value)) {
            nicknameError.textContent = '사용 불가능한 닉네임입니다.';
            nicknameError.classList.add('show');
            nicknameSuccess.classList.remove('show');
        } else if (this.value.length > 0 && validateNickname(this.value)) {
            nicknameError.classList.remove('show');
            nicknameSuccess.textContent = '사용 가능한 닉네임입니다.';
            nicknameSuccess.classList.add('show');
        } else {
            nicknameError.classList.remove('show');
            nicknameSuccess.classList.remove('show');
        }
        
        checkSubmitBtn();
    });

    // 프로필 이미지 클릭
    profilePreview.addEventListener('click', function() {
        profileImage.click();
    });

    // 프로필 이미지 선택
    profileImage.addEventListener('change', function() {
        profileError.textContent = '';
        profileError.classList.remove('show');
        
        const file = this.files[0];

        if (file) {
            // 파일 확장자 검사
            const fileName = file.name.toLowerCase();
            const allowedExtensions = ['.png', '.jpg', '.jpeg', '.gif'];
            const isValidExtension = allowedExtensions.some(ext => fileName.endsWith(ext));

            if (!isValidExtension) {
                // 유효하지 않은 파일 형식
                showConfirmModal('다음 형식의 이미지만 사용할 수 있습니다.\n *.png, .jpg, .jpeg, .gif*');
                this.value = ''; // 파일 입력 초기화
                return;
            }

            // 파일 크기 체크 (5MB)
            if (file.size > 5 * 1024 * 1024) {
                profileError.textContent = '이미지 크기가 5MB를 초과해 사용할 수 없습니다.';
                profileError.classList.add('show');
                this.value = '';
                return;
            }

            profileError.classList.remove('show');

            // 미리보기
            const reader = new FileReader();
            reader.onload = function(e) {
                previewImg.src = e.target.result;
                previewImg.style.display = 'block';
                plusIcon.style.display = 'none';
                removeProfileBtn.style.display = 'flex';
            };
            reader.readAsDataURL(file);
        }
    });

    // 프로필 이미지 삭제 버튼
    if (removeProfileBtn) {
        removeProfileBtn.addEventListener('click', function(e) {
            e.stopPropagation();
            profileImage.value = '';
            previewImg.src = '';
            previewImg.style.display = 'none';
            plusIcon.style.display = 'block';
            removeProfileBtn.style.display = 'none';
            profileError.classList.remove('show');

            profileError.textContent = '';
            profileError.classList.remove('show');
        });
    }

    // 회원가입 버튼 활성화 체크
    function checkSubmitBtn() {
        const isPasswordValid = validatePassword(password.value);
        const isPasswordMatch = password.value === passwordConfirm.value && passwordConfirm.value.length > 0;
        const isNicknameValid = validateNickname(nickname.value);
        
        if (isEmailVerified && isPasswordValid && isPasswordMatch && isNicknameValid) {
            submitBtn.disabled = false;
            overallError.classList.remove('show');
        } else {
            submitBtn.disabled = true;
        }
    }

    // 취소 버튼 클릭
    cancelBtn.addEventListener('click', function() {
        location.href = '/main/';
    });

    // 폼 제출
    signupForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        if (!submitBtn.disabled) {
            try {
                // 이메일 조합
                const domainValue = domainSelect.value === 'custom' ? customDomain.value.trim() : domainSelect.value;
                const fullEmail = emailId.value.trim() + '@' + domainValue;
                
                const formData = new FormData();
                formData.append('email', fullEmail);
                formData.append('password', password.value);
                formData.append('nickname', nickname.value);
                
                // 프로필 이미지가 있으면 추가
                if (profileImage && profileImage.files.length > 0) {
                    formData.append('profile_image', profileImage.files[0]);
                }
                
                const response = await fetch('/uauth/signup-api/', {
                    method: 'POST',
                    body: formData
                });
                
                const data = await response.json();
                
                if (data.success) {
                    // 성공 모달 표시
                    successModal.classList.add('show');
                } else {
                    overallError.textContent = data.message || '회원가입에 실패했습니다.';
                    overallError.classList.add('show');
                }
            } catch (error) {
                console.error('Signup error:', error);
                overallError.textContent = '서버 오류가 발생했습니다.';
                overallError.classList.add('show');
            }
        }
    });
});

// 모달 확인 버튼 클릭
modalConfirmBtn.addEventListener('click', function() {
    successModal.classList.remove('show');
    window.location.href = '/main';
});