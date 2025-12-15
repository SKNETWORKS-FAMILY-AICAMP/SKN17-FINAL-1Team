document.addEventListener("DOMContentLoaded", function () {
  const wrappers = document.querySelectorAll(".image-wrapper");
  let openMenu = null;

  // 삭제 확인 모달
  const deleteModal = document.getElementById("deleteModal");
  const deleteCancelBtn = document.getElementById("deleteCancelBtn");
  const deleteConfirmBtn = document.getElementById("deleteConfirmBtn");
  let targetItemForDelete = null;

//   1) ... 버튼 & 작은 메뉴 모달
  wrappers.forEach(function (wrapper) {
    const menuBtn = wrapper.querySelector(".image-menu-btn");
    const menu = wrapper.querySelector(".image-menu");
    const img = wrapper.querySelector(".gallery-image");
    if (!menuBtn || !menu || !img) return;

    // ... 버튼 클릭: 메뉴 열기/닫기
    menuBtn.addEventListener("click", function (event) {
      event.stopPropagation();

      if (openMenu && openMenu !== menu) {
        openMenu.classList.remove("is-open");
      }

      const isOpen = menu.classList.contains("is-open");
      if (isOpen) {
        menu.classList.remove("is-open");
        openMenu = null;
      } else {
        menu.classList.add("is-open");
        openMenu = menu;
      }
    });

    const saveBtn = menu.querySelector(".image-menu-item.save");
    const deleteBtn = menu.querySelector(".image-menu-item.delete");

    // "이미지 저장" 클릭
    if (saveBtn) {
      saveBtn.addEventListener("click", function (event) {
        event.stopPropagation();
        handleImageSave(menu, img);
        closeOpenMenu();
      });
    }

    // "이미지 삭제" 클릭
    if (deleteBtn) {
      deleteBtn.addEventListener("click", function (event) {
        event.stopPropagation();
        targetItemForDelete = wrapper.closest(".gallery-item");
        openDeleteModal();
        closeOpenMenu();
      });
    }
  });

  // 화면 아무 데나 클릭하면 열린 메뉴 닫기
  document.addEventListener("click", function () {
    closeOpenMenu();
  });

  // 어떤 메뉴든 열려있는 메뉴 닫는 함수
  function closeOpenMenu() {
    if (openMenu) {
      openMenu.classList.remove("is-open");
      openMenu = null;
    }
  }

//   2) 이미지 저장 (파일 탐색기)
  async function handleImageSave(menu, img) {
    const imageSrc = img.getAttribute("src");
    const filename = img.dataset.filename;
    console.log(filename)
    // 브라우저 보안상 경로를 바로 쓸 수는 없고,
    // 다운로드 대화상자를 띄워서 유저가 경로/이름 고르게 하는 방식.
    try {
      const res = await fetch(imageSrc);
      const blob = await res.blob();

      const url = URL.createObjectURL(blob);

      const a = document.createElement("a");
      a.href = url;
      a.download = filename;
      document.body.appendChild(a);
      a.click();
      a.remove();
      URL.revokeObjectURL(url);

      console.log("디버그 - 저장 완료")
    } catch (err) {
        console.error("이미지 저장 오류:", err);
        alert("이미지 저장 중 문제가 발생했습니다.");
    }
  }

//   3) 이미지 삭제 모달
  function openDeleteModal() {
    if (!deleteModal) return;
    deleteModal.classList.add("is-open");
    document.body.classList.add("no-scroll");
  }

  function closeDeleteModal() {
    if (!deleteModal) return;
    deleteModal.classList.remove("is-open");
    document.body.classList.remove("no-scroll");
    targetItemForDelete = null;
  }

  if (deleteCancelBtn) {
    deleteCancelBtn.addEventListener("click", function () {
      closeDeleteModal();
    });
  }

  if (deleteConfirmBtn) {
    deleteConfirmBtn.addEventListener("click", async () => {
      if (!targetItemForDelete) return;
      
      const del_img = targetItemForDelete.querySelector('.gallery-image');
      const imageId = del_img?.dataset.imageId;
      
      console.log(del_img);
      
      if (!imageId) {
        alert('이미지 ID를 찾을 수 없습니다.');
        closeDeleteModal();
        return;
      }
      // formData.append('image_id', imageId);
      
      try {
        const res = await fetch('delete', {
          method: 'POST',
          body: JSON.stringify({
            'image_id': imageId
          }),
          headers: {
            "Content-Type": "application/json",
            'X-CSRFToken': getCookie('csrftoken')
          }
        });

        const data = await res.json();
        console.log(data);

        if (data.success) {
          // DOM 에서 이미지 제거
          console.log('in success');
          targetItemForDelete.remove();

          // 이미지가 하나도 없으면 페이지 새로고침
          const remainingImages = document.querySelectorAll('.gallery-item');
          if (remainingImages.length === 0) window.location.reload();
        } else {
          console.log('in else')
          alert(data.message || '이미지 삭제 실패');
        }
      } catch (err) {
        console.error('오류 디버깅: ', err);
        alert('이미지 삭제 중 문제 발생');
      } finally {
        closeDeleteModal();
      }
    });
  }


  if (deleteModal) {
    deleteModal.addEventListener("click", function (event) {
      if (event.target === deleteModal) {
        closeDeleteModal();
      }
    });
  }

  // CSRF 토큰 가져오기
  function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
      const cookies = document.cookie.split(';');
      for (let i = 0; i < cookies.length; i++) {
        const cookie = cookies[i].trim();
        if (cookie.substring(0, name.length + 1) === (name + '=')) {
          cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
          break;
        }
      }
    }
    return cookieValue;
  }
});
