# pa tests

# curl -X GET "http://localhost:8000/api/features/standtime?userID=101&now=2021-01-18T13:42:44.000Z"

# curl -X GET "http://localhost:8000/api/features/standtime?userID=101&window=1d&now=2021-01-19T22:42:44.000Z"

# curl -X GET "http://localhost:8000/api/features/standtime?userID=101&window=4d&now=2021-01-19T22:42:44.000Z"

# curl -X GET "http://localhost:8000/api/features/standtime?userID=101&window=4d&now=2021-01-19T22:42:44.000Z"

# curl -X GET "http://localhost:8000/api/features/standtime?userID=101&window=4d&now=2021-01-19T22:42:44.000Z"

# curl -X GET "http://localhost:8000/api/features/stepcount?userID=101&window=4d&now=2021-01-19T22:42:44.000Z"


curl -X GET "http://localhost:8000/api/features/pa?type=stand_time&userID=101&now=2021-01-18T13:42:44.000Z"
echo -e "\n"

curl -X GET "http://localhost:8000/api/features/pa?type=step_time&userID=101&window=1d&now=2021-01-19T22:42:44.000Z"
echo -e "\n"

curl -X GET "http://localhost:8000/api/features/pa?type=upr_time&userID=101&window=4d&now=2021-01-19T22:42:44.000Z"
echo -e "\n"

curl -X GET "http://localhost:8000/api/features/pa?type=sed_time&userID=101&window=4d&now=2021-01-19T22:42:44.000Z"
echo -e "\n"

curl -X GET "http://localhost:8000/api/features/pa?type=stand_time&userID=101&window=4d&now=2021-01-19T22:42:44.000Z"
echo -e "\n"

curl -X GET "http://localhost:8000/api/features/pa?type=stepcount&userID=101&window=4d&now=2021-01-19T22:42:44.000Z"
echo -e "\n"


# sleep quality tests
curl -X GET "http://localhost:8000/api/features/sq?userID=101&now=2021-01-20T22:42:44.000Z"

# demographics tests

curl -X GET 'http://localhost:8000/api/features/demographics?user_id=101'

# ema tests

# curl -X GET 'http://localhost:8000/api/features/ema?userID=101&type=mindfulness&lastn=3&now=2021-01-19T22:42:44.000Z'
# curl -X GET 'http://localhost:8000/api/features/ema?userID=101&type=per_cog&lastn=5&now=2021-01-19T22:42:44.000Z'
USER_ID=101
LASTN=3
NOW="2021-01-19T22:42:44.000Z"
TYPES=("mindfulness" "per_cog" "calm" "tired" "lonely" "pain" "control" "feel" "where_now" "whowith_now" "negative_affect" "high_arousal_pos")
for type in "${TYPES[@]}"; do
  echo "Requesting type=$type"
  curl -X GET "http://localhost:8000/api/features/ema?userID=${USER_ID}&type=${type}&lastn=${LASTN}&now=${NOW}"
  echo -e "\n"
done