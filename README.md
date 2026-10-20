# Body Metrics

Enter smart-scale-style body composition into Garmin Connect when you don't have a smart scale. Garmin's own app only lets you enter weight; this lets you add BMI, body fat, body water, muscle mass, bone mass, visceral fat, metabolic age, BMR and physique rating.

Each measurement is uploaded the same way a smart scale does it, so the values show up on the weight screen in Garmin Connect.

## Install (Windows)

1. Go to the [latest release](https://github.com/slipx06/garmin-body-metrics/releases/latest) and download **BodyMetrics-Setup-x.y.z.exe**.
2. Run it. Windows may show **"Windows protected your PC"** because the app isn't signed by a paid certificate. Click **More info**, then **Run anyway**.
3. Click through the installer. It doesn't need admin rights and can put a shortcut on your desktop.
4. Body Metrics opens in your browser. Sign in with your Garmin email and password.

You don't need Python or anything else installed.

To stop the app, click **Close app** at the top of the page. To uninstall it, use **Settings → Apps → Installed apps**.

## Using it

- **Several people:** click **+ Add person** to sign in another Garmin account. The buttons at the top switch between people, and the page shows whose account you're entering for.
- **Two-step verification** is supported.
- **BMI** is worked out from weight and height. Each person's height and kg/lb choice are remembered.
- **History:** the last 30 days of weigh-ins from Garmin Connect are shown under the form.

## Updates

The Garmin sign-in library is unofficial and sometimes breaks when Garmin changes its login. When a fixed version is released, the app shows a banner with a download link. Run the new installer over the old one; everyone stays signed in.

## Privacy

Everything runs on your own computer. Your password goes only to Garmin and is never stored. Login tokens are saved in `%USERPROFILE%\.garminconnect\profiles\`, one folder per person, and signing a person out deletes theirs. If something goes wrong, the installed app writes a log to `%USERPROFILE%\.garminconnect\body-metrics.log`.

## Running from source

Needs Python 3.10 or later.

```
pip install -r requirements.txt
python app.py
```

Or double-click `Body Metrics.bat`. Run `Create Shortcut.bat` once to put a shortcut to it on your desktop; run it again if you move the folder.

If the app is already running, starting it again just opens another browser tab. To load code changes, click **Close app** first.

If signing in stops working, run `pip install -U garminconnect`.

## Building the installer

The [build workflow](.github/workflows/build.yml) builds the installer on GitHub:

- **Pull requests** build a test installer. Download it from the run's **Artifacts** section.
- **Releases:** update `__version__` in `app.py`, commit, then tag and push:

  ```
  git tag v1.1.0
  git push origin v1.1.0
  ```

  The workflow builds the installer and publishes it as a GitHub release, which is what the update banner checks.

To build locally you need [PyInstaller](https://pyinstaller.org) and [Inno Setup 6](https://jrsoftware.org/isinfo.php):

```
pip install pyinstaller
pyinstaller --noconfirm packaging/body_metrics.spec
iscc /DAppVersion=1.1.0 packaging\installer.iss
```

The installer is written to `dist\`.

## Credits

Uses the unofficial [python-garminconnect](https://github.com/cyberjunky/python-garminconnect) library. Not affiliated with Garmin.
