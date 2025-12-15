document.addEventListener('DOMContentLoaded', function() {
    const agreeAll = document.getElementById('agreeAll');
    const agreePrivacy = document.getElementById('agreePrivacy');
    const agreeTerms = document.getElementById('agreeTerms');
    const nextBtn = document.getElementById('nextBtn');
    const requiredTerms = document.querySelectorAll('.required-term');

    // 다음 버튼 활성화/비활성화 체크
    function checkAllTerms() {
        const allChecked = agreePrivacy.checked && agreeTerms.checked;
        nextBtn.disabled = !allChecked;
        
        // 모두 동의 체크박스 상태 업데이트
        agreeAll.checked = allChecked;
    }

    // 모두 동의 체크박스 클릭 시
    agreeAll.addEventListener('change', function() {
        const isChecked = this.checked;
        agreePrivacy.checked = isChecked;
        agreeTerms.checked = isChecked;
        checkAllTerms();
    });

    // 개별 약관 체크박스 클릭 시
    requiredTerms.forEach(function(checkbox) {
        checkbox.addEventListener('change', function() {
            checkAllTerms();
        });
    });

    // 다음 버튼 클릭 시
    nextBtn.addEventListener('click', function() {
        if (!this.disabled) {
            // 다음 단계로 이동
            location.href = "/uauth/signup/form/";
        }
    });
});
