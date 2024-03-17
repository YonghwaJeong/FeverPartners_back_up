//뒤로가기
function goBack() {
    window.history.back();
}

//group_activity에서 ajax 처리
function loadContent(url) {
    fetch(url)
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.text();
    })
    .then(data => {
        document.getElementById('group-activity-content').innerHTML = data;
    })
    .catch(error => {
        console.error('Error during fetch operation:', error);
    });
}

function changeTab(tab, event, room_id) {
    event.preventDefault();

    // 모든 링크에서 selected-group-tab 클래스 제거
    var links = document.querySelectorAll('#group-select-activity-list a');
    links.forEach(function(link) {
    link.classList.remove('selected-group-tab');
    });

    // 클릭한 링크에 selected-group-tab 클래스 추가
    var selectedLink = event.currentTarget;
    selectedLink.classList.add('selected-group-tab');


    var url = '';
    switch (tab) {
    case 'member':
        url = window.location.origin + '/group_activity/member_list/'+room_id;
        break;
    case 'activate':
        url = window.location.origin + '/group_activity/activate/'+room_id;
        break;
    case 'show_log':
        url = window.location.origin + '/group_activity/show_log/'+room_id;
        break;
    }
    loadContent(url);
}

//기본 페이지 설정
function defaultActivate(roomId) {
    loadContent('../member_list/'+roomId);
  }

function authActivate(roomId) {
    loadContent(window.location.origin + '/group_activity/activate/'+roomId);
    var links = document.querySelectorAll('#group-select-activity-list a');
    links.forEach(function(link) {
    link.classList.remove('selected-group-tab');
    });
    const authSpaceTab = document.getElementById('auth-space');
    authSpaceTab.classList.add('selected-group-tab');
}


//그룹 관리 탭 ajax
function loadContentManage(url) {
    fetch(url)
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.text();
    })
    .then(data => {
        document.getElementById('group-admin-content').innerHTML = data;
        runScriptsInContent(data);
    })
    .catch(error => {
        console.error('Error during fetch operation:', error);
    });
}

function runScriptsInContent(htmlContent) {
    const scripts = Array.from(new DOMParser().parseFromString(htmlContent, 'text/html').querySelectorAll('script'));
    scripts.forEach(script => {
        const newScript = document.createElement('script');
        newScript.text = script.text;
        document.body.appendChild(newScript);
    });
}

function changeTabManage(tab, event, room_id) {
    event.preventDefault();

    // 모든 링크에서 selected-group-admin-tab 클래스 제거
    var links = document.querySelectorAll('.nav a');
    links.forEach(function(link) {
    link.classList.remove('selected-group-admin-tab');
    });

    // 클릭한 링크에 selected-group-admin-tab 클래스 추가
    var selectedLink = event.currentTarget;
    selectedLink.classList.add('selected-group-admin-tab');


    var url = '';
    switch (tab) {
    case 'member_list':
        url = '../member_list/'+room_id;
        break;
    case 'direct_invitation':
        url = '../direct_invitation/'+room_id;
        break;
    case 'verify':
        url = '../../group_activity/verify/'+room_id;
        break;
    }
    loadContentManage(url);
}

//기본 페이지 설정
function defaultActivateManage(roomId) {
    loadContentManage('../member_list/'+roomId);
}

//인증 마감(delete)
function closeAuth(roomId, authId) {
    Swal.fire({
      title: "인증을 마감하시겠습니까?",
      text: "마감한 인증은 복구할 수 없어요!",
      icon: "warning",
      showCancelButton: true,
      confirmButtonColor: "#3085d6",
      cancelButtonColor: "#d33",
      confirmButtonText: "마감",
      cancelButtonText: "취소",
    }).then((result) => {
        if (result.isConfirmed) {
            fetch("../close_auth/" + roomId + "/" + authId , {
                method: "DELETE",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": getCookie("csrftoken"),
                },
            })
                .then((response) => {
                    if (response.ok) {
                        const authElement = document.getElementById('auth-' + authId);
                        authElement.remove();
                        return response.json();
                    } else {
                        Swal.fire({
                            title: "삭제 실패",
                            text: "인증 삭제 중 오류가 발생했습니다",
                            icon: "error",
                        });
                        throw new Error("삭제 과정에서 오류가 발생했습니다.");
                    }
                })
                .then((json_data) => {
                    Swal.fire({
                        title: "마감 완료",
                        text: json_data.message,
                        icon: "success",
                    });
                })
                .catch(error => { console.log(error.message)})
      } else if (result.dismiss === Swal.DismissReason.cancel) {
        Swal.fire({
          title: "취소됨",
          text: "인증 마감이 취소되었습니다.",
          icon: "error",
          confirmButtonText: "확인",
        });
      }
    });
}

function acceptAuth(authId, roomId) {
    closeModal()
    fetch(window.location.origin + "/group_activity/accept_auth_log/" + authId)
    .then(response => {
        if (response.ok) {
            loadContentManage(window.location.origin + '/group_activity/verify/'+roomId);
        }
    })
} 

function refuseAuth(authId, roomId) {
    closeModal()
    fetch(window.location.origin + "/group_activity/refuse_auth_log/" + authId)
    .then(response => {
        if (response.ok) {
            loadContentManage(window.location.origin + '/group_activity/verify/'+roomId);
        }
    })
} 