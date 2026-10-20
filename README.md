# Body Metrics

A small local web app for entering smart-scale-style body composition into Garmin Connect when you don't have a smart scale. Garmin's own app only lets you enter weight; this lets you add BMI, body fat, body water, muscle mass, bone mass, visceral fat, metabolic age, BMR and physique rating.

It uses the unofficial [python-garminconnect](https://github.com/cyberjunky/python-garminconnect) library and uploads each measurement the same way a smart scale does, so the values show up on the weight screen in Garmin Connect.

## Setup

```
pip install -r requirements.txt
```

## Run

Double-click `Body Metrics.bat`, or run:

```
python app.py
```

It opens http://127.0.0.1:5000 in your browser. Close the command window to stop it.

## Features

- Several people can each add their own Garmin account and switch between them. The page clearly shows whose account you're entering for.
- Supports Garmin two-step verification.
- Works out BMI from weight and height. Each person's height and kg/lb choice are remembered.
- Shows the last 30 days of weigh-ins from Garmin Connect.

## Where logins are stored

Login tokens are saved in `~/.garminconnect/profiles/`, one folder per person. Passwords are never stored. Signing a person out deletes their tokens.

## Note

The Garmin library is unofficial and can break when Garmin changes its login. If signing in stops working, run `pip install -U garminconnect`.
