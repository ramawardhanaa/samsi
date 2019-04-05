from flask import Flask, render_template, jsonify, request
from sensorlib.scale import Scale
from helper.logging_activity import Log
from helper.api_data import ApiData

log = Log()
try:
    scale = Scale()  # Scale for /api data
except Exception as e:
    log.write_log("something went wrong with the scale!: {}".format(e))

app = Flask(__name__)


@app.route('/')
def start():
    cal = scale.calibrated()
    error = scale.has_error()
    return render_template('start.html', title="start", calibrated=cal, error=error)


@app.route('/log')  # reading log file
def read_log():
    file = open("/var/www/upload/log.txt", "r")
    f = file.readlines()
    print(f)
    return render_template('log.html', title="debug mode", log_content=f)


@app.route('/calibrate')  # start calibrate the scale
def calibrate():
    scale.setup()
    return render_template('calibrate.html', title="calibrate")


@app.route('/calibrate_offset')  # calibrate the offset starting
def calibrate_offset():
    return render_template('calibrate_offset.html', title="calibrate offset")


@app.route('/quick_start')  # start quick calibrate the scale
def quick_start():
    return render_template('quick_start.html', title="quick start")


@app.route('/quick_setup')
def quick_setup():
    scale.calibrate(10000)  # quick calibrate the scale with 10 Kg
    cal = scale.calibrated()
    return render_template('calibrated.html', title="calibrate offset", calibrated=cal, error=scale.has_error())


@app.route('/calibrate_offset', methods=['POST'])  # send known weight to calibrate
def config_scale():
    scale.calibrate(request.form['weight'])
    cal = scale.calibrated()
    return render_template('calibrated.html', title="calibrated", calibrated=cal)


@app.route('/settings')  # setting page
def settings():
    return render_template('settings.html', title="setting")


@app.route('/settings', methods=['POST'])
def setting():
    # is tare or reset posted to settings?
    error = False
    try:
        if request.form.get("reset") == "":
            scale.reset()
        if request.form.get("tare") == "":
            scale.tare()

    except Exception as error:
        log.write_log("settings went wrong: {}".format(error))
    return render_template('settings.html', title="setting", error=error)


@app.route('/api')  # need api data to debug sensors
def summary():
    json_data = ""
    try:
        api_data = ApiData()
        json_data = api_data.get_data()
        weight = scale.get_data()
        json_data["weight"] = "{0} {1}".format(weight, "KG")
    except Exception as error:
        log.write_log("call /api went wrong: {}".format(error))
        json_data["error"] = "{}".format(error)

    return jsonify(
        data=json_data,
    )


if __name__ == '__main__':
    app.run(host='0.0.0.0')
