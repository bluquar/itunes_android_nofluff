itunes_android_nofluff
======================

There are a bunch of solutions out there for syncing your iTunes library with your Android device, but in my experience they are all cumbersome, limiting, or unreliable. This program does what you need: copies files from your Unix machine to your Android device.

*WARNING* Although this program is reliable and effective, it does take some time and know-how to set up. If you have never written code, you may have some trouble.

Setup:
------

1. Install the [Android SDK](http://developer.android.com/sdk/index.html)
2. Ensure you have [Python 2.7 or 3.4](https://www.python.org/download/) installed
3. [Enable developer options](http://developer.android.com/tools/device.html) on your Android device
  * Android 3.2 or older: Settings > Applications > Development.
  * Android 4.0 and newer: Settings > Developer options.
    + Note: On Android 4.2 and newer, Developer options is hidden by default. To make it available, go to Settings > About phone and tap Build number seven times. Return to the previous screen to find Developer options.
4. Clone this repository (or download the files in it)
5. Set the configuration options in sync_music.py
  * The comments in this file describe what each option means

Use:
----

1. Enable USB debugging on your device in Developer options
2. Connect your device to your Unix machine via USB
3. Run `python sync_music.py`
4. A dialog box should appear on your phone asking if you trust the computer
  * Hit yes if you do
  * You will only need to complete this step the first time
5. Wait for the transfer to complete
  * If you have `DBG_VERB` enabled in your configuration, you should see a flood of file transfer reports
6. Disable USB debugging
  * There is some controversy about whether you actually need to do this
    + *If you leave USB debugging on, a thief can get past your lock screen with adb*. Be aware of this
    + [Discussion of pros and cons of leaving USB debugging on](http://android.stackexchange.com/questions/16250/what-is-usb-debugging-can-i-keep-it-on-forever)


