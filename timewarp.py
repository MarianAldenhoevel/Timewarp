"""
    This is the main module of the timewarp video processor.

    Copyright (c) 2017 Marian Aldenhövel


    See the following sites for more information. 

    https://marian-aldenhoevel.de/timewarp
    https://github.com/MarianAldenhoevel/Timewarp

    Published under the MIT license, see https://github.com/MarianAldenhoevel/Timewarp/blob/master/LICENSE
"""

import argparse
import json
import math
import numpy
from scipy.interpolate import interp1d
import skvideo.io

def generateoutputframe():
    # construct a new frame for the output. This pulls in data from
    # the newest frame (last in the frames array) and previous ones.
    #
    # The top line of the output frame comes from the most recent frame
    # while later lines may be from older frames, creating the effect
    # that the lower you go the older the data is.
    #
    # The source frame for a line is selected by mapping the line
    # index on the delta requested by the user. If a frame does not
    # exist use the latest one (first in the list).
    #
    # This results in the first frame generated being equal to the first
    # frame of the input video. Then time starts to pass at the top of
    # the frame. At some point down the line the bottom row is args.delta
    # frame behind and that is the steady state for the middle part
    # of the source video.
    #
    # To wind up we then continue generating frames while still dropping
    # from the start this causes the bottom of the generated video to
    # "catch up" with the top.
    
    # start with a copy of the most recent frame.
    newframe = frames[-1].copy()

    # Q: From what frame do we take row n?
    # A: The top row from -1, the last, most recent one.
    # the bottom row should be args.delta frames in the past,
    # so for instance -25 for the default value. Implement
    # as linear interpolation.
    rows = newframe.shape[0]   
    srcframe_func = interp1d([0,rows], [-1, -args.delta])
   
    for row in range(rows):
        srcframe = srcframe_func(row)
        
        # srcframe will likely lie between two actual frames.
        # We want to compute an weighted average between the two
        # So find two integer srcframes and the weight to sum them
        # with
        weight = math.fabs(math.modf(srcframe)[0])
        srcframe0 = int(math.floor(srcframe))
        srcframe1 = int(math.ceil(srcframe))

        # If the requested source is further back than
        # we have data use the earliest we have. Note that the two
        # srcframes are at most 1 apart, so either one will be clamped
        # to be the same as the other or both will be clamped to a
        # third one and be the same frame as well. So the weighted sum 
        # still works.
        if srcframe0 < -len(frames):
            srcframe0 = -len(frames)
        if srcframe1 < -len(frames):
            srcframe1 = -len(frames)

        # Compute row for the new frame as weighted sum of the
        # corresponding rows from both source frames
        sources = numpy.array([frames[srcframe0][row],frames[srcframe1][row]])
        newrow = numpy.average(sources, weights = [weight, 1-weight], axis = 0)
        newrow = newrow.astype(frames[srcframe0][row].dtype)

        # Put the new row into the new frame
        newframe[row] = newrow 
        
    # write out the result as frame in the output video.
    writer.writeFrame(newframe)

# Setup command line parser
parser = argparse.ArgumentParser(description = "Create a timewarped version of a video file.")
parser.add_argument("-v", "--verbose", default = 0,           dest = "verbosity",  action = "count",             help = "Increase verbosity (repeat for more output)")
parser.add_argument("-i", "--input",                          dest = "inputfile",  required = True,              help = "name of input file with video readable by sk-video/ffmpeg")
parser.add_argument("-o", "--output",  default= "output.mp4", dest = "outputfile",                               help = "name of output file")
parser.add_argument("-d", "--delta",   default = 25,          dest = "delta",                        type = int, help = "time-delta between top and bottom of frame in source-frames")
args = parser.parse_args()

# Probe input file.
if args.verbosity >= 1:
    print "Probing file \"{0:s}\"...".format(args.inputfile)

# Dump video metadata at appropriate verbosity-levels
video_metadata = skvideo.io.ffprobe(args.inputfile)

if args.verbosity >= 1:
    print "Video format detected: width={0}pixel, height={1}pixel, framerate={2}".format(
    video_metadata["video"]["@width"],
    video_metadata["video"]["@height"],
    video_metadata["video"]["@r_frame_rate"])

if args.verbosity >= 2:
    print json.dumps(video_metadata, indent = 4)

# Open input file ar generator to read each frame in turn.
if args.verbosity >= 1:
    print "Reading file \"{0:s}\"...".format(args.inputfile)

inputparameters = {}
outputparameters = {}
reader = skvideo.io.FFmpegReader(args.inputfile,
    inputdict=inputparameters,
    outputdict=outputparameters)

try:
    # Open video writer for output
    if args.verbosity >= 1:
        print "Writing to file \"{0:s}\"...".format(args.outputfile)

    writer = skvideo.io.FFmpegWriter(args.outputfile)

    frames = []

    # iterate through the frames
    frame_index = 0
    for frame in reader.nextFrame():
        frame_index = frame_index + 1

        if (args.verbosity >= 2) or (frame_index%100 == 0):
            print "Processing frame #{0}...".format(frame_index)
        
        # append new frame to the buffer of frames
        frames.append(frame)
        
        # once we have enough frames buffered we drop the first
        # one.
        if len(frames) > args.delta:
            frames.pop(0)

        generateoutputframe()

    # all frames consumed, now wind up by generating one more
    # for each one left in the buffer
    if args.verbosity >= 1:
        print "Winding up buffer..."

    frames.pop()
    while (len(frames) > 0):
        generateoutputframe()
        frames.pop(0)
        
finally:
    if args.verbosity >= 1:
        print "Closing output file..."

    writer.close()
