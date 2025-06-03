from helper.validator import httpTimeOutValidator

def test_http_time_out_validator_success():
    result = httpTimeOutValidator('183.215.23.242:9091')

if __name__ == '__main__':
    test_http_time_out_validator_success()
