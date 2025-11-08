from flask import Flask, render_template, request, jsonify, send_file
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.proxies import WebshareProxyConfig
import os
from datetime import datetime
import re
import json
from openai import OpenAI

app = Flask(__name__)

# OpenAI API 설정
# 환경 변수에서 API 키를 가져옵니다
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
if not OPENAI_API_KEY:
    print("경고: OPENAI_API_KEY 환경 변수가 설정되지 않았습니다.")
    print("GPT 기능을 사용하려면 .env 파일에 API 키를 설정하세요.")
    OPENAI_API_KEY = "dummy-key-for-testing"
client = OpenAI(api_key=OPENAI_API_KEY)

# 폴더 설정
TRANSCRIPT_FOLDER = 'transcripts'
HISTORY_FOLDER = 'history'
if not os.path.exists(TRANSCRIPT_FOLDER):
    os.makedirs(TRANSCRIPT_FOLDER)
if not os.path.exists(HISTORY_FOLDER):
    os.makedirs(HISTORY_FOLDER)


def extract_video_id(url_or_id):
    """
    유튜브 URL 또는 비디오 ID에서 비디오 ID를 추출합니다.
    """
    # 이미 비디오 ID인 경우
    if len(url_or_id) == 11 and not ('/' in url_or_id or '.' in url_or_id):
        return url_or_id
    
    # URL 패턴 매칭
    patterns = [
        r'(?:youtube\.com\/watch\?v=)([a-zA-Z0-9_-]{11})',
        r'(?:youtu\.be\/)([a-zA-Z0-9_-]{11})',
        r'(?:youtube\.com\/embed\/)([a-zA-Z0-9_-]{11})',
        r'(?:youtube\.com\/v\/)([a-zA-Z0-9_-]{11})'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url_or_id)
        if match:
            return match.group(1)
    
    return url_or_id


def get_transcript(video_id, languages=['ko', 'en']):
    """
    유튜브 비디오의 자막을 추출합니다.
    """
    try:
        # Webshare 프록시 설정으로 YouTubeTranscriptApi 인스턴스 생성
        proxy_username = os.getenv('WEBSHARE_PROXY_USERNAME', 'your-username')
        proxy_password = os.getenv('WEBSHARE_PROXY_PASSWORD', 'your-password')
        
        ytt_api = YouTubeTranscriptApi(
            proxy_config=WebshareProxyConfig(
                proxy_username=proxy_username,
                proxy_password=proxy_password,
            )
        )
        
        # fetch 메서드를 사용하여 자막 가져오기
        transcript = ytt_api.fetch(video_id, languages=languages)
        
        return transcript, None
    
    except Exception as e:
        return None, str(e)


def format_transcript(transcript):
    """
    자막을 포맷팅합니다. 3분 단위로 타임스탬프를 표시하고 텍스트를 한 덩어리로 만듭니다.
    """
    snippets = transcript.snippets if hasattr(transcript, 'snippets') else transcript
    
    # 3분 단위로 그룹화
    grouped_transcript = []
    current_group = {
        'timestamp': '00:00',
        'texts': []
    }
    current_minute_group = 0
    
    for entry in snippets:
        timestamp = entry.start if hasattr(entry, 'start') else entry['start']
        text = entry.text if hasattr(entry, 'text') else entry['text']
        
        minutes = int(timestamp // 60)
        minute_group = (minutes // 3) * 3  # 3분 단위로 그룹화 (0, 3, 6, 9, ...)
        
        # 새로운 3분 그룹이 시작되면
        if minute_group != current_minute_group and current_group['texts']:
            # 이전 그룹 저장
            grouped_transcript.append({
                'timestamp': current_group['timestamp'],
                'text': ' '.join(current_group['texts'])
            })
            # 새 그룹 시작
            current_group = {
                'timestamp': f"{minute_group:02d}:00",
                'texts': [text]
            }
            current_minute_group = minute_group
        else:
            # 같은 그룹에 텍스트 추가
            if not current_group['texts']:
                current_group['timestamp'] = f"{minute_group:02d}:00"
            current_group['texts'].append(text)
            current_minute_group = minute_group
    
    # 마지막 그룹 추가
    if current_group['texts']:
        grouped_transcript.append({
            'timestamp': current_group['timestamp'],
            'text': ' '.join(current_group['texts'])
        })
    
    return grouped_transcript


def check_spelling_with_gpt(text):
    """
    GPT를 사용하여 맞춤법을 검사하고 수정합니다.
    """
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": """당신은 전문 교정자입니다. 주어진 텍스트의 맞춤법, 띄어쓰기, 문법을 검사하고 수정해주세요.
                    
규칙:
1. 맞춤법 오류를 수정합니다
2. 띄어쓰기를 올바르게 수정합니다
3. 문법적 오류를 수정합니다
4. 자연스러운 문장으로 다듬습니다
5. 원문의 의미는 절대 변경하지 않습니다
6. 타임스탬프 형식 [MM:SS]는 그대로 유지합니다
7. 수정된 텍스트만 출력하고, 설명이나 부가 정보는 포함하지 않습니다"""
                },
                {
                    "role": "user",
                    "content": f"다음 텍스트의 맞춤법을 검사하고 수정해주세요:\n\n{text}"
                }
            ],
            temperature=0.3,
            max_tokens=4000
        )
        
        corrected_text = response.choices[0].message.content.strip()
        return corrected_text, None
    
    except Exception as e:
        return None, str(e)


def summarize_with_gpt(full_text):
    """
    GPT를 사용하여 전체 자막 내용을 요약하고 예시/사례를 추출합니다.
    """
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": """당신은 전문 콘텐츠 분석가입니다. 주어진 동영상 자막을 분석하여 다음을 제공해주세요:

1. 전체 요약: 동영상의 핵심 내용을 3-5문단으로 요약
2. 주요 포인트: 핵심 내용을 불릿 포인트로 정리 (5-10개)
3. 예시 및 사례: 동영상에서 언급된 구체적인 예시, 사례, 사례 연구가 있다면 별도로 추출

다음 JSON 형식으로 응답해주세요:
{
    "summary": "전체 요약 내용",
    "key_points": [
        "주요 포인트 1",
        "주요 포인트 2",
        ...
    ],
    "examples": [
        {
            "title": "예시 제목",
            "description": "예시 설명",
            "timestamp": "언급된 시간대 (있다면)"
        },
        ...
    ]
}

예시나 사례가 없다면 examples 배열을 비워두세요.
JSON 형식만 출력하고, 다른 설명은 포함하지 마세요."""
                },
                {
                    "role": "user",
                    "content": f"다음 동영상 자막을 분석해주세요:\n\n{full_text}"
                }
            ],
            temperature=0.5,
            max_tokens=2000
        )
        
        result = response.choices[0].message.content.strip()
        
        # JSON 파싱
        # 코드 블록으로 감싸져 있을 수 있으므로 제거
        if result.startswith('```'):
            result = result.split('```')[1]
            if result.startswith('json'):
                result = result[4:]
            result = result.strip()
        
        summary_data = json.loads(result)
        return summary_data, None
    
    except json.JSONDecodeError as e:
        return None, f"JSON 파싱 오류: {str(e)}"
    except Exception as e:
        return None, str(e)


def save_transcript_to_file(transcript, video_id):
    """
    자막을 파일로 저장합니다. 3분 단위로 타임스탬프를 표시하고 텍스트를 한 덩어리로 만듭니다.
    """
    snippets = transcript.snippets if hasattr(transcript, 'snippets') else transcript
    
    filename = f"transcript_{video_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    filepath = os.path.join(TRANSCRIPT_FOLDER, filename)
    
    # 3분 단위로 그룹화
    grouped_data = {}
    
    for entry in snippets:
        timestamp = entry.start if hasattr(entry, 'start') else entry['start']
        text = entry.text if hasattr(entry, 'text') else entry['text']
        
        minutes = int(timestamp // 60)
        minute_group = (minutes // 3) * 3  # 3분 단위로 그룹화
        
        if minute_group not in grouped_data:
            grouped_data[minute_group] = []
        grouped_data[minute_group].append(text)
    
    # 파일에 쓰기
    with open(filepath, 'w', encoding='utf-8') as f:
        for minute_group in sorted(grouped_data.keys()):
            timestamp = f"[{minute_group:02d}:00]"
            combined_text = ' '.join(grouped_data[minute_group])
            f.write(f"{timestamp} {combined_text}\n\n")
    
    return filename, filepath


def save_history(video_id, video_url, transcript_data, corrected_data=None):
    """
    히스토리를 저장합니다.
    """
    history_file = os.path.join(HISTORY_FOLDER, 'history.json')
    
    # 기존 히스토리 로드
    if os.path.exists(history_file):
        with open(history_file, 'r', encoding='utf-8') as f:
            history = json.load(f)
    else:
        history = []
    
    # 새 히스토리 항목 추가
    history_item = {
        'id': len(history) + 1,
        'video_id': video_id,
        'video_url': video_url,
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'transcript_count': len(transcript_data),
        'has_correction': corrected_data is not None
    }
    
    history.insert(0, history_item)  # 최신 항목을 맨 앞에 추가
    
    # 최대 100개 항목만 유지
    if len(history) > 100:
        history = history[:100]
    
    # 히스토리 저장
    with open(history_file, 'w', encoding='utf-8') as f:
        json.dump(history, f, ensure_ascii=False, indent=2)
    
    return history_item


def load_history():
    """
    히스토리를 로드합니다.
    """
    history_file = os.path.join(HISTORY_FOLDER, 'history.json')
    
    if os.path.exists(history_file):
        with open(history_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []


@app.route('/')
def index():
    """
    메인 페이지
    """
    return render_template('index.html')


@app.route('/extract', methods=['POST'])
def extract():
    """
    자막 추출 API
    """
    try:
        data = request.get_json()
        url_or_id = data.get('url', '')
        use_spell_check = data.get('use_spell_check', False)
        use_summary = data.get('use_summary', False)
        
        if not url_or_id:
            return jsonify({'error': 'URL 또는 비디오 ID를 입력해주세요.'}), 400
        
        # 비디오 ID 추출
        video_id = extract_video_id(url_or_id)
        
        # 자막 가져오기
        transcript, error = get_transcript(video_id)
        
        if error:
            return jsonify({'error': f'자막을 가져오는 중 오류가 발생했습니다: {error}'}), 500
        
        if not transcript:
            return jsonify({'error': '자막을 찾을 수 없습니다.'}), 404
        
        # 자막 포맷팅
        formatted_transcript = format_transcript(transcript)
        
        # 맞춤법 검사 (옵션)
        corrected_transcript = None
        if use_spell_check:
            corrected_transcript = []
            for item in formatted_transcript:
                corrected_text, error = check_spelling_with_gpt(item['text'])
                if error:
                    # 오류 발생 시 원본 사용
                    corrected_transcript.append({
                        'timestamp': item['timestamp'],
                        'text': item['text'],
                        'corrected': False,
                        'error': error
                    })
                else:
                    corrected_transcript.append({
                        'timestamp': item['timestamp'],
                        'text': corrected_text,
                        'original': item['text'],
                        'corrected': True
                    })
        
        # 요약 및 예시 추출 (옵션)
        summary_data = None
        if use_summary:
            # 전체 텍스트 결합
            full_text = ' '.join([item['text'] for item in formatted_transcript])
            summary_data, error = summarize_with_gpt(full_text)
            if error:
                summary_data = {
                    'error': error,
                    'summary': '요약을 생성할 수 없습니다.',
                    'key_points': [],
                    'examples': []
                }
        
        # 파일로 저장
        filename, filepath = save_transcript_to_file(transcript, video_id)
        
        # 히스토리 저장
        save_history(video_id, url_or_id, formatted_transcript, corrected_transcript)
        
        response_data = {
            'success': True,
            'video_id': video_id,
            'transcript': formatted_transcript,
            'total_count': len(formatted_transcript),
            'filename': filename
        }
        
        if corrected_transcript:
            response_data['corrected_transcript'] = corrected_transcript
        
        if summary_data:
            response_data['summary'] = summary_data
        
        return jsonify(response_data)
    
    except Exception as e:
        return jsonify({'error': f'예상치 못한 오류가 발생했습니다: {str(e)}'}), 500


@app.route('/history', methods=['GET'])
def get_history():
    """
    히스토리 조회 API
    """
    try:
        history = load_history()
        return jsonify({
            'success': True,
            'history': history,
            'total': len(history)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/download/<filename>')
def download(filename):
    """
    자막 파일 다운로드
    """
    try:
        filepath = os.path.join(TRANSCRIPT_FOLDER, filename)
        if os.path.exists(filepath):
            return send_file(filepath, as_attachment=True, download_name=filename)
        else:
            return jsonify({'error': '파일을 찾을 수 없습니다.'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    print("="*80)
    print("유튜브 자막 추출 웹 애플리케이션")
    print("="*80)
    print("\n서버가 시작되었습니다!")
    print("브라우저에서 http://localhost:8080 으로 접속하세요.\n")
    app.run(debug=True, host='0.0.0.0', port=8080)

