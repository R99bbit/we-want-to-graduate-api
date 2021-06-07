# 인공지능 혈압 예측 시스템 API 서버

## usage

```bash
$ pip3 install -r requirements.txt
$ python3 app.py
```

---

## summary

- 해당 API 서버는 E4 스마트 밴드를 통해 측정된 일련의 데이터들을 자동으로 수집하고 엔드포인트 사용자에게 전송하는 역할을 한다.
- Restful 하게 구현되어 있다.
- Flask 기반이다.

---

## API 명세

### [GET] /all_session_info

- 해당 계정의 모든 측정 정보 요약

### [GET] /last_session_info

- 해당 계정의 최근 측정 정보

### [GET] /get_last_session

- 해당 계정의 최근 측정 데이터를 JSON으로 받아옴.