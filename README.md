# 🎬 YouTube Transcript Extractor & Summarizer

유튜브 동영상의 자막을 추출하고, GPT를 활용하여 맞춤법 검사, 요약, 예시 추출까지 제공하는 웹 애플리케이션입니다.

## ✨ 주요 기능

### 1. 자막 추출
- 유튜브 URL 또는 비디오 ID 입력만으로 자막 자동 추출
- 3분 단위로 타임스탬프 그룹화
- 한국어, 영어 자막 우선 지원
- Webshare 프록시를 통한 안정적인 요청 (IP 차단 우회)

### 2. GPT 맞춤법 검사 ✨
- OpenAI GPT-4o-mini 모델 사용
- 맞춤법, 띄어쓰기, 문법 자동 교정
- 원본과 교정본 비교 가능
- 원본 의미 유지하며 자연스럽게 다듬기

### 3. GPT 요약 및 예시 추출 📝
- **전체 요약**: 동영상 핵심 내용을 3-5문단으로 요약
- **주요 포인트**: 5-10개의 핵심 내용 불릿 포인트로 정리
- **예시 및 사례**: 동영상에서 언급된 구체적인 예시 자동 추출
  - 예시 제목
  - 상세 설명
  - 언급 시간대

### 4. 히스토리 관리 📜
- 자막 추출 기록 자동 저장
- 최대 100개 항목 저장
- 히스토리에서 클릭하여 빠른 재추출

### 5. 파일 다운로드 📥
- 추출된 자막을 텍스트 파일로 다운로드
- 타임스탬프 포함

## 🚀 설치 및 실행

### 1. 저장소 클론

```bash
git clone https://github.com/kccho88/youtubesummary.git
cd youtubesummary
```

### 2. 필요한 라이브러리 설치

```bash
pip install -r requirements.txt
```

### 3. 환경 설정

`app.py` 파일에서 다음 설정을 확인/수정하세요:

- **OpenAI API 키**: 13번째 줄
- **Webshare 프록시 인증 정보**: 47-50번째 줄

### 4. 웹 서버 실행

```bash
python app.py
```

### 5. 브라우저 접속

```
http://localhost:8080
```

## 📖 사용 방법

### 기본 자막 추출
1. 유튜브 URL 또는 비디오 ID 입력
2. "자막 추출" 버튼 클릭
3. 결과 확인 및 다운로드

### 맞춤법 검사 사용
1. 유튜브 URL 입력
2. ✅ "GPT 맞춤법 검사 사용" 체크
3. "자막 추출" 버튼 클릭
4. 원본/교정본 탭으로 비교

### 요약 및 예시 추출
1. 유튜브 URL 입력
2. ✅ "GPT 요약 및 예시 추출" 체크
3. "자막 추출" 버튼 클릭
4. "📝 요약 및 예시" 탭에서 확인

### 모든 기능 사용
1. 유튜브 URL 입력
2. ✅ "GPT 맞춤법 검사 사용"
3. ✅ "GPT 요약 및 예시 추출"
4. "자막 추출" 버튼 클릭
5. 3개 탭에서 결과 비교

## 🎯 활용 시나리오

- **강의 영상 정리**: 핵심 내용 + 예시 노트 필기
- **튜토리얼 분석**: 단계별 요약 + 예시 코드 추출
- **프레젠테이션 요약**: 주요 메시지 + 사례 연구
- **인터뷰 분석**: 내용 요약 + 구체적 경험 추출
- **리뷰 정리**: 핵심 평가 + 실제 사용 예시

## 🛠️ 기술 스택

- **Backend**: Flask (Python)
- **Frontend**: HTML5, CSS3, JavaScript (Vanilla)
- **AI**: OpenAI GPT-4o-mini
- **자막 API**: youtube-transcript-api
- **프록시**: Webshare Residential Proxy
- **데이터 저장**: JSON (히스토리)

## 📁 프로젝트 구조

```
youtubesummary/
├── app.py                          # Flask 웹 서버
├── youtube_transcript_extractor.py # CLI 버전
├── templates/
│   └── index.html                 # 웹 인터페이스
├── transcripts/                   # 자막 파일 저장 (자동 생성)
├── history/                       # 히스토리 저장 (자동 생성)
│   └── history.json              # 히스토리 데이터
├── requirements.txt               # 필요한 라이브러리
├── .gitignore                     # Git 제외 파일
└── README.md                      # 프로젝트 설명서
```

## ⚙️ API 엔드포인트

### POST /extract
자막 추출 및 GPT 처리

**요청:**
```json
{
  "url": "유튜브 URL 또는 비디오 ID",
  "use_spell_check": false,
  "use_summary": false
}
```

**응답:**
```json
{
  "success": true,
  "video_id": "비디오ID",
  "transcript": [...],
  "corrected_transcript": [...],
  "summary": {
    "summary": "전체 요약",
    "key_points": [...],
    "examples": [...]
  },
  "filename": "transcript_비디오ID_날짜시간.txt"
}
```

### GET /history
히스토리 조회

### GET /download/<filename>
자막 파일 다운로드

## ⚠️ 주의사항

### 1. API 키 설정
- OpenAI API 키가 필요합니다
- `app.py` 파일의 13번째 줄에서 설정
- 프로덕션 환경에서는 환경 변수 사용 권장

### 2. 프록시 설정
- Webshare 프록시 계정이 필요합니다
- `app.py` 파일의 47-50번째 줄에서 설정
- IP 차단 우회를 위해 사용

### 3. 처리 시간 및 비용
- **맞춤법 검사**: 3분 구간당 약 2-5초
- **요약 및 예시 추출**: 약 3-10초
- GPT API 사용 시 비용 발생
- 자막 길이에 비례하여 비용 증가

### 4. 히스토리
- 로컬에 저장 (`history/history.json`)
- 최대 100개 항목 유지
- 파일 삭제 시 히스토리 초기화

## 🔒 보안

- API 키를 코드에 직접 포함하지 마세요
- 환경 변수 또는 별도의 설정 파일 사용 권장
- `.gitignore`에 민감한 정보 포함 파일 추가
- 프로덕션 환경에서는 `debug=False` 설정

## 📝 라이선스

MIT License

## 🤝 기여

이슈와 풀 리퀘스트를 환영합니다!

## 📧 문의

프로젝트에 대한 문의사항이 있으시면 이슈를 등록해주세요.

## 🙏 감사의 말

- [youtube-transcript-api](https://github.com/jdepoix/youtube-transcript-api) - 유튜브 자막 추출 API
- [OpenAI](https://openai.com/) - GPT API
- [Flask](https://flask.palletsprojects.com/) - 웹 프레임워크

---

Made with ❤️ by kccho88
