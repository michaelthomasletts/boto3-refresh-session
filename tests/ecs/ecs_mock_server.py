import time

from flask import Flask, jsonify

app = Flask(__name__)


@app.route("/v2/credentials", methods=["GET"])
def credentials():
    now = int(time.time())
    return jsonify(
        {
            "AccessKeyId": "<YOUR ACCESS KEY ID HERE>",
            "SecretAccessKey": "<YOUR SECRET ACCESS KEY HERE>",
            "Token": "<YOUR TOKEN HERE>",
            "Expiration": time.strftime(
                "%Y-%m-%dT%H:%M:%SZ", time.gmtime(now + 3600)
            ),
        }
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=1338)
