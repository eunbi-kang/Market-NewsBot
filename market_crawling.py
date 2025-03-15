import requests
from bs4 import BeautifulSoup
import pandas as pd
import os
from dotenv import load_dotenv
import time
import p
import json

# 저장할 디렉토리
SAVE_DIR = "data"
if not os.path.exists(SAVE_DIR):
    os.makedirs(SAVE_DIR)  # 폴더 생성

# 저장할 파일 경로
CSV_PATH = os.path.join(SAVE_DIR, "news_data_full.csv")
PICKLE_PATH = os.path.join(SAVE_DIR, "news_data_full.pkl")
JSON_PATH = os.path.join(SAVE_DIR, "news_data_full.json")

# 기존 파일 삭제
for file in [CSV_PATH, PICKLE_PATH, JSON_PATH]:
    if os.path.exists(file):
        os.remove(file)

# 기본 URL
BASE_URL = "https://www.yna.co.kr/market-plus/all/{}"

# .env 파일 로드
load_dotenv()

# 환경 변수에서 User-Agent 가져오기
HEADERS = {
    "User-Agent": os.getenv("USER_AGENT", "Mozilla/5.0")  # 기본값 설정 가능
}


def get_news_data():
    all_data = []
    page = 1  # 첫 페이지부터 시작

    while True:
        url = BASE_URL.format(page)
        response = requests.get(url, headers=HEADERS)

        if response.status_code != 200:
            print(f"페이지 {page} 요청 실패: {response.status_code}")
            break  # 요청 실패 시 종료

        soup = BeautifulSoup(response.text, "html.parser")

        # 뉴스 리스트 찾기
        news_list = soup.select("div.list-type212 ul.list01 > li")

        # 마지막 페이지 감지 (li 태그가 없으면 종료)
        if not news_list:
            print(f"✅ 마지막 페이지 도달: {page - 1} 페이지까지 크롤링 완료")
            break

        for news in news_list:
            data_cid = news.get("data-cid", "").strip()

            # 이미지 URL 추출
            img_tag = news.select_one("figure.img-con01 img")
            image_url = img_tag["src"] if img_tag else ""

            # 뉴스 제목과 링크
            title_tag = news.select_one("strong.tit-wrap a span.title01")
            title = title_tag.get_text(strip=True) if title_tag else ""

            # 뉴스 요약 (summary) 추출
            summary_tag = news.select_one("p.lead")
            summary = summary_tag.get_text(strip=True) if summary_tag else ""

            # 날짜 추출
            date_tag = news.select_one("span.txt-time")
            date = date_tag.get_text(strip=True) if date_tag else ""

            all_data.append({
                "data_cid": data_cid,
                "image_url": image_url,
                "title": title,
                "summary": summary,
                "date": date
            })

        print(f"페이지 {page} 크롤링 완료")
        page += 1  # 다음 페이지로 이동
        time.sleep(1)  # 요청 속도 조절

    return all_data


if __name__ == "__main__":
    news_data = get_news_data()

    # DataFrame 변환
    df = pd.DataFrame(news_data)

    # CSV 저장
    df.to_csv(CSV_PATH, index=False, encoding="utf-8-sig")

    # Pickle 저장
    with open(PICKLE_PATH, "wb") as f:
        pickle.dump(news_data, f)

    # JSON 저장
    with open(JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(news_data, f, ensure_ascii=False, indent=4)

    print("✅ 모든 페이지 크롤링 완료, 데이터 저장 완료!")
    print(f"📁 저장 경로: {SAVE_DIR}/news_data_full.csv, .pkl, .json")
