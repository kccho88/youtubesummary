# 유튜브 자막 추출 웹 애플리케이션

Flask 기반의 유튜브 자막 추출 웹 애플리케이션입니다.

## 기능

- 🎬 웹 브라우저에서 유튜브 URL 입력
- 📝 실시간 자막 추출 및 표시
- 📥 자막 텍스트 파일 다운로드
- 🎨 현대적이고 반응형 UI 디자인
- ⚡ Webshare 프록시를 통한 안정적인 요청

## 설치 방법

1. 필요한 라이브러리를 설치합니다:

```bash
pip install -r requirements.txt
```

또는 개별 설치:

```bash
pip install youtube-transcript-api>=1.1.1
pip install flask>=2.3.0
```

## 실행 방법

1. 웹 서버를 시작합니다:

```bash
python app.py
```

2. 브라우저에서 다음 주소로 접속합니다:

```
http://localhost:5000
```

3. 유튜브 URL 또는 비디오 ID를 입력하고 "자막 추출" 버튼을 클릭합니다.

## 사용 방법

### 1. URL 입력
다음과 같은 형식의 URL을 입력할 수 있습니다:
- `https://www.youtube.com/watch?v=비디오ID`
- `https://youtu.be/비디오ID`
- `비디오ID` (11자리)

### 2. 자막 추출
- "자막 추출" 버튼을 클릭하면 자동으로 자막을 가져옵니다
- 타임스탬프와 함께 자막이 표시됩니다
- 한국어와 영어 자막을 우선적으로 검색합니다

### 3. 파일 다운로드
- "자막 파일 다운로드" 버튼을 클릭하여 텍스트 파일로 저장할 수 있습니다
- 파일명 형식: `transcript_비디오ID_날짜시간.txt`

## 프로젝트 구조

```
YouTube Transcript1/
├── app.py                          # Flask 웹 애플리케이션
├── youtube_transcript_extractor.py # CLI 버전 프로그램
├── requirements.txt                # 필요한 라이브러리 목록
├── templates/
│   └── index.html                 # 웹 페이지 템플릿
├── transcripts/                   # 자막 파일 저장 폴더
├── README.md                      # CLI 버전 설명서
└── README_WEB.md                  # 웹 버전 설명서 (이 파일)
```

## API 엔드포인트

### POST /extract
자막을 추출합니다.

**요청:**
```json
{
  "url": "유튜브 URL 또는 비디오 ID"
}
```

**응답 (성공):**
```json
{
  "success": true,
  "video_id": "비디오ID",
  "transcript": [
    {
      "timestamp": "00:00",
      "text": "자막 텍스트"
    }
  ],
  "total_count": 61,
  "filename": "transcript_비디오ID_20250108_150000.txt"
}
```

**응답 (실패):**
```json
{
  "error": "오류 메시지"
}
```

### GET /download/<filename>
저장된 자막 파일을 다운로드합니다.

## 기술 스택

- **Backend**: Flask (Python)
- **Frontend**: HTML5, CSS3, JavaScript (Vanilla)
- **API**: youtube-transcript-api
- **프록시**: Webshare Residential Proxy

## 주요 특징

### 1. 프록시 설정
- Webshare 프록시를 사용하여 IP 차단 우회
- 안정적인 자막 추출 보장

### 2. 반응형 디자인
- 모바일, 태블릿, 데스크톱 모든 기기에서 최적화된 UI
- 현대적인 그라데이션 디자인

### 3. 사용자 친화적 인터페이스
- 실시간 로딩 상태 표시
- 명확한 오류 메시지
- 예시 URL 제공

### 4. 파일 관리
- 자동으로 `transcripts/` 폴더에 파일 저장
- 타임스탬프가 포함된 고유한 파일명 생성

## 문제 해결

### 포트가 이미 사용 중인 경우
`app.py` 파일의 마지막 줄에서 포트 번호를 변경하세요:

```python
app.run(debug=True, host='0.0.0.0', port=5001)  # 5000 → 5001
```

### 자막을 찾을 수 없는 경우
- 해당 비디오에 자막이 없을 수 있습니다
- 비디오가 비공개이거나 삭제되었을 수 있습니다
- 프록시 설정을 확인하세요

### 프록시 오류가 발생하는 경우
- Webshare 계정의 프록시 설정을 확인하세요
- `app.py`의 프록시 인증 정보를 확인하세요

## 보안 고려사항

- 프로덕션 환경에서는 `debug=False`로 설정하세요
- 프록시 인증 정보를 환경 변수로 관리하는 것을 권장합니다
- HTTPS를 사용하여 배포하세요

## 라이선스

MIT License

## 참고 문서

- [youtube-transcript-api GitHub](https://github.com/jdepoix/youtube-transcript-api)
- [Flask 공식 문서](https://flask.palletsprojects.com/)

