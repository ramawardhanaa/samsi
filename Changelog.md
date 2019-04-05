# 1.1
## Datalogger:
* The software for collecting data is now decoupled from the web server
* In the event of a crash, the logger restarts automatically
* Improvement of the log file (it becomes even clearer what went wrong, incl. Timestamp)
* The system tries to generate a valid record three times. If the record is invalid after the third time, the RPi restarts and tries again.

## Web server
* From now on you can read the log file under `/ log` (or at the bottom of the navigation on the activity symbol)
* If the scale is not connected correctly, it will be visible during calibration