# Timewarp
The [rolling shutter effect](https://en.wikipedia.org/wiki/Rolling_shutter) is an artifact in digital still photography and video that originates in the fact that a frame is displayed "at once", but recorded by progressively scanning the sensor. That means in a typical video frame taken by a digital camera the bottom parts show the world at a later time than the top parts. This becomes apparent when objects in the scene move fast in relation to the scanning rate of the camera. 

A slower version of the effect can be observed when using a flat-bed scanner or photocopier: If the original or object on the glass is moved while it is being imaged very similar artifacts can be seen.

The rolling shutter effect has gotten a lot of coverage lately with more and more digital video being produced.

[Matt Parkers](https://www.youtube.com/watch?v=nP1elMR5qjc) video on the subject has reminded me of an experimental film I watched a very long time ago, when video was still analog and only TV-people had the equipment to record it. The film was of a set stage with people slowly moving about it and it was manipulated to show radically different times in different parts of the frame.

*Unfortunately that is all I remember about it, and thus could not find any mention of it on the net, if you happen to know something about it, please let me know.*

It occured to me that today an effect like this should be very easy to produce using digital video as input. So I wrote a little Python program to do it.

[timewarp.py](https://github.com/MarianAldenhoevel/Timewarp/blob/master/timewarp.py) takes one video and produced a timewarped version of it by delaying the bottom row for a given number of frames beyond the top row. The code uses numpy and scikit-video and is bordering on trivial 

# Example
Input video:
[![Watch the video](https://raw.githubusercontent.com/MarianAldenhoevel/Timewarp/master/img/poledance_raw.png)](https://www.youtube.com/watch?v=y2Ps1YbHQD4)

Result after delaying the bottom row by 20 frames:
[![Watch the video](https://raw.githubusercontent.com/MarianAldenhoevel/Timewarp/master/img/poledance_timewarped.png)](https://www.youtube.com/watch?v=z8zBFOQINXM)
