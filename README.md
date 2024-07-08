# 프로젝트 설명

이 프로젝트는 upbit api를 통해 자동으로 코인을 거래하여 수익을 만드는 프로그램입니다.

데이트레이딩 방식을 채택하여 당일 거래를 원칙 자동트레이딩을 합니다.

변동성 돌파 전략과 평균 이동 평균선 그리고 prphet으로 당일 종가 가격을 예측하여 모두 가격이 상승한다는 예측을 하였을 때 구매하는 프로그램으로 안정성이 보장되기는 하나, 거래가 자주 발생하지는 않습니다.


# API Server

src = "./api.png"
- balance : ticker에 해당하는 코인이나 화폐를 현재 보유한 만큼 return합니다.
- best kvalue : 변동성 돌파 전략을 구하는 api로 count 기간 중 브루트포스로 k값을 0.01부터 1까지 탐색하여 최고의 결과를 가진 k 값을 구하고 return합니다.
- buy-market-order : amount만큼을 시장가로 구매하고 return합니다.
- moving-average : 평균 이동 평균선을 조회하여 금액을 return합니다.
- predict-price : Prophet으로 당일 종가 가격을 예측하여 return합니다.
- price : upbit ticker에 해당하는 코인의 현재 가격을 가져와 return합니다.
- sell-market-order : amount만큼을 시장가로 판매하고 return합니다.
- start-time : 시작 시간 조회하고 return합니다.
- target-price :  k값을 통해 매수 목표가를 계산하여 return합니다.

## windows 기준 환경설정

pip install python 3.9.5

pip install numpy 1.26.4

pip install pystan  2.19.1.1

pip install cython 3.0.10

 pip install cmdstanpy 1.2.2

 pip install prophet 1.1.5

pip install flask 2.2.2

pip install flask-restx 1.3.0

pip install pyupbit 0.2.33
