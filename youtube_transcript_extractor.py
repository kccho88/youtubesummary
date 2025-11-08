from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.proxies import WebshareProxyConfig
import sys


def extract_video_id(url_or_id):
    """
    유튜브 URL 또는 비디오 ID에서 비디오 ID를 추출합니다.
    """
    if 'youtube.com' in url_or_id or 'youtu.be' in url_or_id:
        if 'v=' in url_or_id:
            return url_or_id.split('v=')[1].split('&')[0]
        elif 'youtu.be/' in url_or_id:
            return url_or_id.split('youtu.be/')[1].split('?')[0]
    return url_or_id


def get_transcript(video_id, languages=['ko', 'en']):
    """
    유튜브 비디오의 자막을 추출합니다.
    
    Args:
        video_id: 유튜브 비디오 ID
        languages: 선호하는 언어 리스트 (기본값: 한국어, 영어)
    
    Returns:
        자막 데이터 리스트
    """
    try:
        # Webshare 프록시 설정으로 YouTubeTranscriptApi 인스턴스 생성
        ytt_api = YouTubeTranscriptApi(
            proxy_config=WebshareProxyConfig(
                proxy_username="kccho888",
                proxy_password="websharekccho888754",
            )
        )
        
        # fetch 메서드를 사용하여 자막 가져오기
        transcript = ytt_api.fetch(video_id, languages=languages)
        
        return transcript
    
    except Exception as e:
        print(f"오류 발생: {str(e)}")
        return None


def print_transcript(transcript):
    """
    자막을 보기 좋게 출력합니다.
    """
    if not transcript:
        print("자막을 가져올 수 없습니다.")
        return
    
    print("\n" + "="*80)
    print("자막 내용")
    print("="*80 + "\n")
    
    # FetchedTranscript 객체에서 snippets 리스트 가져오기
    snippets = transcript.snippets if hasattr(transcript, 'snippets') else transcript
    
    for entry in snippets:
        # 객체의 속성으로 접근
        timestamp = entry.start if hasattr(entry, 'start') else entry['start']
        text = entry.text if hasattr(entry, 'text') else entry['text']
        
        # 시간을 분:초 형식으로 변환
        minutes = int(timestamp // 60)
        seconds = int(timestamp % 60)
        
        print(f"[{minutes:02d}:{seconds:02d}] {text}")
    
    print("\n" + "="*80)
    print(f"총 {len(snippets)}개의 자막 항목")
    print("="*80)


def save_transcript_to_file(transcript, filename="transcript.txt"):
    """
    자막을 파일로 저장합니다.
    """
    if not transcript:
        print("저장할 자막이 없습니다.")
        return
    
    try:
        # FetchedTranscript 객체에서 snippets 리스트 가져오기
        snippets = transcript.snippets if hasattr(transcript, 'snippets') else transcript
        
        with open(filename, 'w', encoding='utf-8') as f:
            for entry in snippets:
                # 객체의 속성으로 접근
                timestamp = entry.start if hasattr(entry, 'start') else entry['start']
                text = entry.text if hasattr(entry, 'text') else entry['text']
                
                minutes = int(timestamp // 60)
                seconds = int(timestamp % 60)
                
                f.write(f"[{minutes:02d}:{seconds:02d}] {text}\n")
        
        print(f"\n자막이 '{filename}' 파일로 저장되었습니다.")
    
    except Exception as e:
        print(f"파일 저장 중 오류 발생: {str(e)}")


def main():
    """
    메인 함수
    """
    print("="*80)
    print("유튜브 자막 추출 프로그램")
    print("="*80)
    
    # 비디오 ID 또는 URL 입력 받기
    if len(sys.argv) > 1:
        video_input = sys.argv[1]
    else:
        video_input = input("\n유튜브 비디오 ID 또는 URL을 입력하세요: ")
    
    # 비디오 ID 추출
    video_id = extract_video_id(video_input)
    print(f"\n비디오 ID: {video_id}")
    print("자막을 가져오는 중...\n")
    
    # 자막 가져오기
    transcript = get_transcript(video_id)
    
    if transcript:
        # 자막 출력
        print_transcript(transcript)
        
        # 파일로 저장할지 물어보기
        try:
            save_option = input("\n자막을 파일로 저장하시겠습니까? (y/n): ")
            if save_option.lower() == 'y':
                filename = input("파일명을 입력하세요 (기본값: transcript.txt): ").strip()
                if not filename:
                    filename = "transcript.txt"
                save_transcript_to_file(transcript, filename)
        except EOFError:
            # 입력을 받을 수 없는 환경에서는 자동으로 저장
            filename = f"transcript_{video_id}.txt"
            print(f"\n자동으로 파일을 저장합니다...")
            save_transcript_to_file(transcript, filename)
    else:
        print("자막을 가져오지 못했습니다.")


if __name__ == "__main__":
    main()

