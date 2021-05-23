:cat: html파일에 nav-bar style="url(' ... ')" => 상대경로로두니까 url get요청으로 넘어가버려서 인스턴스내의 절대경로로 img 경로 잡아줘야함

### issue ex)

`url_for('public') {{'css/style.css'}}` =====> base.html

drivingInfo.html에서도 base.html을 사용하고

drivingInfo/<string: driving_date>/<string: start> 에서도 base.html을 사용하는데



drivingInfo.html에서 drivingInfo/public/css/style.css로 img를 가져오고

drivingInfo/<string: driving_date>/<string: start> 에서 drivingInfo/<string: driving_date>/<string: start>/public/css/style.css 로 img를 GET으로 가져와서(flask 서버 로그보면 나옴!) 그냥 절대경로로 잡아줘야할 것 같음



:cat: app.py에 app.run() ip주소확인!



