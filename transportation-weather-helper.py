from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import datetime
import time

# 現在日付・時刻取得
now = datetime.datetime.now()
current_time = now.strftime("%Y/%m/%d %H:%M")

chrome_options = Options()
#chrome_options.add_argument("--headless=new")   # テストの時コメントアウト
chrome_options.add_argument("--window-size=1920,1080")
driver = webdriver.Chrome(options=chrome_options)

#########################
# 丸ノ内線の運行状況をチェック
#########################

# 東京メトロの運行情報URL
driver.get("https://www.tokyometro.jp/index.html")
wait = WebDriverWait(driver, 10)

# 「運行状況」をクリック」
button = wait.until(
    EC.element_to_be_clickable((By.CSS_SELECTOR, ".v2_gnavUnkouStatusSummary a"))
)
button.click()

# 「運行状況」見えるまでに待つ
wait.until(
    EC.presence_of_element_located((By.CSS_SELECTOR, ".v2_routeList li"))
)

print("\n"+"="*20+f"{current_time} Tokyo Metro🚃の運行状況"+"="*20)

route_items = driver.find_elements(By.CSS_SELECTOR, ".v2_routeList li")
for item in route_items:
    line_elem = item.find_elements(By.CSS_SELECTOR, ".v2_linkIcon a")
    status_elem = item.find_elements(By.CSS_SELECTOR, ".v2_routeListUnkouTxt")

    # 運行状況以外のv2_linkIconをスキップ
    if not line_elem or not status_elem:
        continue

    line_name = line_elem[0].text.strip()
    status = status_elem[0].text.strip()

    if line_name == "丸ノ内線":
        if status == "平常運転":
            print(f"丸ノ内線 → ✅ {status}")
        else:
            print(f"丸ノ内線 → ❌ {status}")

################################
# 新宿線・大江戸線の運行状況をチェック
################################
driver.get("https://www.kotsu.metro.tokyo.jp/subway/schedule/")

wait = WebDriverWait(driver, 10)

wait.until(
    EC.presence_of_element_located((By.CSS_SELECTOR, ".operation__item"))
)

print("\n"+"="*20+f"{current_time} 都営地下鉄🚇の運行状況"+"="*20)

items = driver.find_elements(By.CSS_SELECTOR, ".operation__item")

for item in items:
    line_name = item.find_element(By.TAG_NAME, "dt").text.strip()
    status = item.find_element(By.CLASS_NAME, "operation__info").text.strip()

    if line_name in ["新宿線", "大江戸線"]:
        if status == "現在、１５分以上の遅延はありません。":
            print(f"{line_name} → ✅ {status}")
        else:
            print(f"{line_name} → ❌ {status}")

######################
# 本日の天気状況をチェック
######################

# 渋谷区の天気データURL
url = "https://tenki.jp/forecast/3/16/4410/13113/1hour.html"
driver.get(url)
wait = WebDriverWait(driver, 10)

# 時刻を生成（01～24）
hours = []
for i in range(1, 25):
    hours.append(f"{i:02d}")

# 「今日（today）」のtableを特定
table = driver.find_element(By.ID, "forecast-point-1h-today")
#table = driver.find_element(By.ID, "forecast-point-1h-tomorrow")
#table = driver.find_element(By.ID, "forecast-point-1h-dayaftertomorrow")

# tableから降水確率の行特定
prob_row = table.find_element(By.CSS_SELECTOR, "tr.prob-precip")
# 降水確率の行から降水確率セル特定
prob_cells = prob_row.find_elements(By.TAG_NAME, "td")

# tableから降水量の行特定
precip_row = table.find_element(By.CSS_SELECTOR, "tr.precipitation")
# 降水量の行から降水量セル特定
precip_cells = precip_row.find_elements(By.TAG_NAME, "td")

# ループ処理
forecast_data = []
for i in range(24):
    prob_span = prob_cells[i].find_element(By.TAG_NAME, "span")
    precip_span = precip_cells[i].find_element(By.TAG_NAME, "span")

    # 過去の時間を見なくて良い
    if "past" in prob_span.get_attribute("class"):
        continue

    hour = hours[i]
    prob = prob_span.text.strip()
    precip = precip_span.text.strip()

    forecast_data.append({
        "hour": hour,
        "prob": int(prob), # 0～100
        "precip": float(precip) # 0.6mm/hなどもあるのでfloat!
    })

print("\n"+"="*20+f"{current_time} 本日の天気☔️状況"+"="*20)

for item in forecast_data:
    prob = item["prob"]
    precip = item["precip"]
    hour = int(item["hour"])

    # ⭐の数で雨の激しさを表現
    if precip >= 20.0:
        stars = "⭐⭐⭐⭐⭐"
    elif precip >= 15.0:
        stars = "⭐⭐⭐⭐"
    elif precip >= 10.0:
        stars = "⭐⭐⭐"
    elif precip >= 3.0:
        stars = "⭐⭐"
    elif precip >= 1.0:
        stars = "⭐"
    else:
        stars = ""

    time_range = f"{hour:02d}:00 ~ {hour:02d}:59"
    print(f"{time_range}  降水確率：{prob:>3}%  降水量：{precip:>4}mm/h  緊急度：{stars}")

driver.quit()
