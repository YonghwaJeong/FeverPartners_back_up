const reportPk = document.getElementById('report-pk-hidden').value;
document.getElementById('report-love-btn').addEventListener('click', () => {
    fetchAndUpdateCounts('love');
  });
  
document.getElementById('report-like-btn').addEventListener('click', () => {
    fetchAndUpdateCounts('like');
  });
  
document.getElementById('report-dislike-btn').addEventListener('click', () => {
    fetchAndUpdateCounts('dislike');
  });
  
function fetchAndUpdateCounts(action) {
    fetch(window.location.origin + '/goal/achievement_report/update_react_count/' + reportPk, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': getCookie('csrftoken'),
        },
      body: JSON.stringify({ action: action })
    })
      .then(response => {
        if (!response.ok) {
          throw new Error('요청을 처리하던 중 서버에서 문제가 발생했습니다.');
        }
        return response.json();
      })
      .then(data => {
        if ('love_count' in data) {
            document.getElementById('report-love-count').innerText = data.love_count;
          }
          if ('like_count' in data) {
            document.getElementById('report-like-count').innerText = data.like_count;
          }
          if ('dislike_count' in data) {
            document.getElementById('report-dislike-count').innerText = data.dislike_count;
          }
      })
      .catch(error => {
        console.error(error);
      });
  }

document.getElementById('report-user-report-btn').addEventListener('click', async () => {
const { value: reason, isDismissed } = await Swal.fire({
    title: '<div style="color: #FF5733">신고하기</div>',
    input: 'radio',
    inputOptions: {
    '1': '광고성/스팸 게시물',
    '2': '불쾌한/부적절한 컨텐츠',
    '3': '어뷰징/적절하지 않은 인증',
    '4': '기타 사유',
    },
    inputValidator: (value) => {
      return new Promise((resolve) => {
        if (value) {
          resolve();
        } else {
          resolve('신고 사유를 선택해주세요.');
        }
      });
    },
    showCancelButton: true,
    cancelButtonText: '취소',
    confirmButtonText: '신고',
    confirmButtonColor: '#FF5733',
});
    if (reason) {
    Swal.fire({
      title: '<div style="font-size: 24px">신고가 완료되었습니다.</div>',
      icon: 'success',
    });
}
});
  